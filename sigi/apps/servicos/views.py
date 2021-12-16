# -*- coding: utf-8 -*-
import csv
import json as simplejson  # XXX trocar isso por simplesmente import json e refatorar o codigo

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.db.models import Q
from django.forms.forms import BoundField
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView

from sigi.apps.casas.models import Orgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.convenios.views import normaliza_data, query_ordena
from sigi.apps.servicos.models import (Servico, TipoServico, CasaManifesta, CasaAtendida,
                                       ServicoManifesto)


class MapaView(TemplateView):

    template_name = "servicos/mapa.html"

    def get_context_data(self, **kwargs):
        context = super(MapaView, self).get_context_data(**kwargs)
        context['servicos'] = TipoServico.objects.all()
        return context


def municipios_atendidos(self, servico):
    municipios = []
    servico = servico.upper()

    query = Q()

    if servico != 'ALL':
        for sigla in servico.split('_'):
            query = query | Q(tipo_servico__sigla=sigla)

    query = Q(data_desativacao=None) & query

    for casa in CasaAtendida.objects.all():
        if casa.servico_set.filter(query).exists():
            m = casa.municipio
            municipio = {'nome': casa.nome + ', ' + m.uf.sigla,
                         'lat': str(m.latitude),
                         'lng': str(m.longitude),
                         'servicos': "<ul><li>" + "</li><li>".join([s.tipo_servico.nome for s in casa.servico_set.filter(query)]) + "</li></ul>", }
            municipios.append(municipio)

    return HttpResponse(simplejson.dumps(municipios), content_type='application/json')


class CasaManifestaProtoForm(forms.Form):
    fieldsets = None
    informante = forms.CharField(max_length=100, required=False)
    cargo = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)

    def set_fieldsets(self, fieldsets):
        result = []
        for name, lines in fieldsets:
            field_lines = []
            for line in lines:
                if isinstance(line, str):
                    line = (line,)
                field_line = []
                for field_name in line:
                    field = self.fields[field_name]
                    bf = BoundField(self, field, field_name)
                    field_line.append(bf)
                field_lines.append(field_line)
            result.append({'name': name, 'lines': field_lines},)
        self.fieldsets = result


def casa_manifesta_view(request):
    if 'casa_id' in request.GET:
        casa_id = request.GET.get('casa_id')
        casa = get_object_or_404(Orgao, pk=casa_id)

        # Criar um formulário dinâmico

        campos = {}
        fieldsets = ((None, ('informante', 'cargo', 'email'),),)

        for ts in TipoServico.objects.all():
            campos['possui_%s' % ts.pk] = forms.BooleanField(label=_(u'Possui o serviço de %s') % ts.nome, required=False)
            campos['url_%s' % ts.pk] = forms.URLField(label=_(u'Informe a URL'), required=False)
            campos['hospedagem_interlegis_%s' % ts.pk] = forms.BooleanField(label=_(u'Serviço está hospedado no Interlegis'), required=False)
            fieldsets += ((ts.nome, ('possui_%s' % ts.pk, 'url_%s' % ts.pk, 'hospedagem_interlegis_%s' % ts.pk)),)

        CasaManifestaForm = type('', (CasaManifestaProtoForm,), campos)

        if request.method == 'POST':
            cmf = CasaManifestaForm(request.POST)
            if cmf.is_valid():
                thanks = []
                cm, created = CasaManifesta.objects.get_or_create(casa_legislativa=casa)
                cm.informante = cmf.cleaned_data['informante']
                cm.cargo = cmf.cleaned_data['cargo']
                cm.email = cmf.cleaned_data['email']
                cm.save()
                thanks.append((_(u'Informante'), cmf.cleaned_data['informante']))
                thanks.append((_(u'Cargo'), cmf.cleaned_data['cargo']))
                thanks.append((_(u'E-mail'), cmf.cleaned_data['email']))
                for ts in TipoServico.objects.all():
                    if cmf.cleaned_data['possui_%s' % ts.pk]:
                        sm, created = ServicoManifesto.objects.get_or_create(casa_manifesta=cm, servico=ts)
                        sm.url = cmf.cleaned_data['url_%s' % ts.pk]
                        sm.hospedagem_interlegis = cmf.cleaned_data['hospedagem_interlegis_%s' % ts.pk]
                        sm.save()
                        thanks.append((ts.nome, _(u'Possui o serviço acessível em %(url)s %(obs)s') % dict(
                            url=sm.url,
                            obs=_(u'hospedado no Interlegis') if sm.hospedagem_interlegis else '')))
                    else:
                        ServicoManifesto.objects.filter(casa_manifesta=cm, servico=ts).delete()
                        thanks.append((ts.nome, _(u'Não possui')))
                extra_context = {'casa': casa, 'thanks': thanks}
            else:
                extra_context = {'casa': casa, 'cmf': cmf}
        else:
            try:
                cm = casa.casamanifesta
                values = {
                    'informante': cm.informante,
                    'cargo': cm.cargo,
                    'email': cm.email,
                }
                for sm in cm.servicomanifesto_set.all():
                    values['possui_%s' % sm.servico.pk] = True
                    values['url_%s' % sm.servico.pk] = sm.url
                    values['hospedagem_interlegis_%s' % sm.servico.pk] = sm.hospedagem_interlegis
                cmf = CasaManifestaForm(values)
            except:
                cmf = CasaManifestaForm()

            cmf.set_fieldsets(fieldsets)

            extra_context = {'casa': casa, 'cmf': cmf}
    elif 'uf' in request.GET:
        uf = request.GET.get('uf')
        extra_context = {'casa_list': Orgao.objects.filter(municipio__uf__sigla=uf)}
    else:
        extra_context = {'uf_list': UnidadeFederativa.objects.all()}

    return render_to_response('servicos/casa_manifesta.html', extra_context, context_instance=RequestContext(request))

def adicionar_servicos_carrinho(request, queryset=None, id=None):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
    if 'carrinho_servicos' not in request.session:
        request.session['carrinho_servicos'] = ids_selecionados
    else:
        lista = request.session['carrinho_servicos']
        # Verifica se id já não está adicionado
        for id in ids_selecionados:
            if id not in lista:
                lista.append(id)
        request.session['carrinho_servicos'] = lista
        
def carrinhoOrGet_for_qs(request):
    """
       Verifica se existe convênios na sessão se não verifica get e retorna qs correspondente.
    """
    if 'carrinho_servicos' in request.session:
        ids = request.session['carrinho_servicos']
        qs = Servico.objects.filter(pk__in=ids)
        qs = qs.order_by("casa_legislativa__municipio__uf", "casa_legislativa__municipio")
        qs = get_for_qs(request.GET, qs)
    else:
        qs = Servico.objects.all()
        if request.GET:
            qs = qs.order_by("casa_legislativa__municipio__uf", "casa_legislativa__municipio")
            qs = get_for_qs(request.GET, qs)
    return qs


def adicionar_servicos_carrinho(request, queryset=None, id=None):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
        if 'carrinho_servicos' not in request.session:
            request.session['carrinho_servicos'] = ids_selecionados
        else:
            lista = request.session['carrinho_servicos']
            # Verifica se id já não está adicionado
            for id in ids_selecionados:
                if id not in lista:
                    lista.append(id)
            request.session['carrinho_servicos'] = lista

@login_required
def excluir_carrinho(request):
    if 'carrinho_servicos' in request.session:
        del request.session['carrinho_servicos']
        messages.info(request, u'O carrinho foi esvaziado')
    return HttpResponseRedirect('../../')

@login_required
def deleta_itens_carrinho(request):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
        if 'carrinho_servicos' in request.session:
            lista = request.session['carrinho_servicos']
            for item in ids_selecionados:
                lista.remove(item)
            if lista:
                request.session['carrinho_servicos'] = lista
            else:
                del lista
                del request.session['carrinho_servicos']

    return HttpResponseRedirect('.')

@login_required
def visualizar_carrinho(request):

    qs = carrinhoOrGet_for_qs(request)

    paginator = Paginator(qs, 100)

    # Make sure page request is an int. If not, deliver first page.
    # Esteja certo de que o `page request` é um inteiro. Se não, mostre a primeira página.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # Se o page request (9999) está fora da lista, mostre a última página.
    try:
        paginas = paginator.page(page)
    except (EmptyPage, InvalidPage):
        paginas = paginator.page(paginator.num_pages)

    carrinhoIsEmpty = not('carrinho_servicos' in request.session)

    return render(
        request,
        'servicos/carrinho.html',
        {
            'carIsEmpty': carrinhoIsEmpty,
            'paginas': paginas,
            'query_str': '?' + request.META['QUERY_STRING']
        }
    )
    
def get_for_qs(get, qs):
    kwargs = {}
    ids = 0
    get._mutable = True
    normaliza_data(get, 'data_ativacao__gte')
    normaliza_data(get, 'data_ativacao__lte')
    get._mutable = False
    for k, v in get.iteritems():
        if k not in ['page', 'pop', 'q', '_popup']:
            if not k == 'o':
                if k == "ot":
                    qs = query_ordena(qs, get["o"], get["ot"])
                else:
                    kwargs[str(k)] = v
                    if(str(k) == 'ids'):
                        ids = 1
                        break
    qs = qs.filter(**kwargs)
    if ids:
        query = 'id IN (' + kwargs['ids'].__str__() + ')'
        qs = Servico.objects.extra(where=[query])
    return qs

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=servicos.csv'

    csv_writer = csv.writer(response)
    servicos = carrinhoOrGet_for_qs(request)
    if not servicos:
        return HttpResponseRedirect('../')

    atributos = [_(u"Casa Legislativa"), _(u"Contato Interlegis"), _(u"Produto"),
                 _(u"Data de Ativação"), ]

    if request.POST:
        atributos = request.POST.getlist("itens_csv_selected")

    col_titles = atributos
    if _(u"Casa Legislativa") in col_titles:
        pos = col_titles.index(_(u"Casa Legislativa")) + 1
        col_titles.insert(pos, _(u"uf"))
        pos+=1
        col_titles.insert(pos, _(u"email"))
        pos+=1
        col_titles.insert(pos, _(u"telefone"))
    
    if _(u"Contato Interlegis") in col_titles:
        pos = col_titles.index(_(u"Contato Interlegis")) + 1
        col_titles.insert(pos, _(u"Email do contato"))
        
    csv_writer.writerow([s.encode("utf-8") for s in col_titles])

    for servico in servicos:
        lista = []
        for atributo in atributos:
            if _(u"Casa Legislativa") == atributo:
                lista.append(servico.casa_legislativa.nome.encode("utf-8"))
                lista.append(servico.casa_legislativa.municipio.uf.sigla.encode("utf-8"))
                lista.append(servico.casa_legislativa.email.encode("utf-8"))
                if servico.casa_legislativa.telefone is not None:
                    lista.append(servico.casa_legislativa.telefone)
                else:
                    lista.append("")
            elif _(u"Contato Interlegis") == atributo:
                if servico.casa_legislativa.contato_interlegis is not None:
                    lista.append(servico.casa_legislativa.contato_interlegis)
                    lista.append(servico.casa_legislativa.contato_interlegis.email.encode("utf-8"))
                else:
                    lista.append("")
                    lista.append("")
            elif _(u"Produto") == atributo:
                lista.append(servico.tipo_servico.nome.encode("utf-8"))
            elif _(u"Data de Ativação") == atributo:
                data = ''
                if servico.data_ativacao:
                    data = servico.data_ativacao.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
            else:
                pass

        csv_writer.writerow(lista)

    return response
