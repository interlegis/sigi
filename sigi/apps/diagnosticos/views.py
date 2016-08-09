# -*- coding: utf-8 -*-
import json as simplejson  # XXX trocar isso por simplesmente import json e refatorar o codigo
from itertools import cycle

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from sigi.apps.casas.models import Funcionario
from sigi.apps.contatos.models import Telefone
from sigi.apps.diagnosticos.decorators import validate_diagnostico
from sigi.apps.diagnosticos.forms import (CasaLegislativaMobileForm,
                                          DiagnosticoMobileForm,
                                          FuncionariosMobileForm)
from sigi.apps.diagnosticos.models import Categoria, Diagnostico, Pergunta
from sigi.apps.diagnosticos.urls import LOGIN_REDIRECT_URL
from sigi.apps.utils.decorators import login_required
from sigi.shortcuts import render_to_pdf


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
def lista(request):
    """Consulta os diagnosticos do servidor logado,
    que contenham o status de não publicado.
    """
    servidor = request.user.servidor
    diagnosticos = servidor.diagnosticos
    context = RequestContext(request, {'diagnosticos': diagnosticos})
    return render_to_response('diagnosticos/diagnosticos_list.html', context)


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
@validate_diagnostico
def categorias(request, id_diagnostico):
    """Consulta as categorias do diagnostico selecionado
    a partir da sua identificação
    """
    categorias = Categoria.objects.all()
    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)

    # Estilizando a lista de categorias para que ajude a identificar
    # qual categoria foi a ultima a ser usada, como também as outras
    # que ainda não foram acessadas
    ultima_categoria = request.session.get('ultima_categoria', 0)

    context = RequestContext(request, {'categorias': categorias,
                                       'diagnostico': diagnostico, 'ultima_categoria': ultima_categoria})
    return render_to_response('diagnosticos/diagnosticos_categorias_list.html',
                              context)


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
@validate_diagnostico
def categoria_detalhes(request, id_diagnostico, id_categoria):
    """Captura as perguntas da categoria
    selecionada. Durante o preenchimento das perguntas, o camada
    template do projeto, vai requisitar a inserção dos campos via
    AJAX a cada mudança de pergunta

    Caso alguma inserção não passe na validação do formulário em
    questão, será enviado as mensagens de erro no formato JSON,
    para que a camada de template do projeto trate-as de forma adequada.
    """

    # Grava na sessão a categoria atual, para destacar que
    # era foi a última visitada.
    request.session['ultima_categoria'] = int(id_categoria)

    try:
        categoria = Categoria.objects.get(pk=id_categoria)
    except Categoria.DoesNotExist:
        context = RequestContext(request)
        return render_to_response('mobile/404.html', context)

    diagnostico = Diagnostico.objects.filter(publicado=False).get(pk=id_diagnostico)

    if request.method == "POST":
        form = DiagnosticoMobileForm(request.POST,
                                     instance=diagnostico, category=id_categoria)
        if form.is_valid():
            form.save()
            resposta = {
                'mensagem': 'sucesso'
            }
        else:
            # Montando a estrutura das mensagens de erro no formato JSON
            resposta = {
                'mensagem': 'erro',
                'erros': form.errors
            }
        json = simplejson.dumps(resposta)
        return HttpResponse(json, content_type='application/json')
    else:
        form = DiagnosticoMobileForm(instance=diagnostico,
                                     category=id_categoria)

    context = RequestContext(request, {'form': form, 'categoria': categoria,
                                       'diagnostico': diagnostico})
    return render_to_response('diagnosticos/diagnosticos_categorias_form.html',
                              context)


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
@validate_diagnostico
def categoria_casa_legislativa(request, id_diagnostico):

    # Grava na sessão a categoria atual, para destacar que
    # era foi a última visitada.
    request.session['ultima_categoria'] = 1

    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    casa_legislativa = diagnostico.casa_legislativa

    if request.method == "POST":
        form = CasaLegislativaMobileForm(request.POST,
                                         instance=casa_legislativa)
        if form.is_valid():
            form.save()
            resposta = {
                'mensagem': 'sucesso'
            }
        else:
            # Montando a estrutura das mensagens de erro no formato JSON
            resposta = {
                'mensagem': 'erro',
                'erros': form.errors
            }
        json = simplejson.dumps(resposta)
        return HttpResponse(json, content_type='application/json')
    else:
        form = CasaLegislativaMobileForm(instance=casa_legislativa)

    context = RequestContext(request, {'form': form,
                                       'diagnostico': diagnostico, 'casa_legislativa': casa_legislativa})
    return render_to_response(
        'diagnosticos/diagnosticos_categoria_casa_legislativa_form.html',
        context)


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
@validate_diagnostico
def categoria_contatos(request, id_diagnostico):

    # Grava na sessão a categoria atual, para destacar que
    # era foi a última visitada.
    request.session['ultima_categoria'] = 2

    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    casa_legislativa = diagnostico.casa_legislativa

    funcionarios = []

    for n, l in Funcionario.SETOR_CHOICES:
        if casa_legislativa.funcionario_set.filter(setor=n).count() <= 1:
            funcionarios.append(casa_legislativa.funcionario_set.get_or_create(setor=n))
        else:
            for f in casa_legislativa.funcionario_set.filter(setor=n):
                funcionarios.append((f, False))

    if request.method == "POST":
        forms = []
        for f, c in funcionarios:
            try:
                forms.append(FuncionariosMobileForm(request.POST, prefix=f.setor, instance=f))
            except:
                pass

        resposta = {
            'mensagem': 'sucesso',
            'erros': {},
            'fones': {},
            'clean': (),
        }

        # valida e salva um formulario por vez
        for form in forms:
            if form.is_valid():
                form.save()
                s = ''
                for form_telefones in form.telefones.forms:
                    tel = form_telefones.instance
                    if tel._state.adding and tel.numero != '':
                        s += _(u'<p>Novo telefone %(type)s: %(number)s</p>') % dict(
                            type=form_telefones.instance.get_tipo_display(),
                            number=form_telefones.instance.numero)
                        resposta['clean'] += ('id_' + form_telefones.prefix + '-numero',)
                if s != '':
                    resposta['fones'][form.prefix] = s
            else:
                # Montando a estrutura das mensagens de erro no formato JSON
                resposta['mensagem'] = 'erro'
                for key, value in form.errors.iteritems():
                    resposta['erros'][form.prefix + '-' + key + '-errors'] = value

                for form_telefones in form.telefones.forms:
                    if not form_telefones.is_valid():
                        if (form_telefones.fields['id'].initial is not None
                                and form_telefones.fields['tipo'].initial == 'I'
                                and form_telefones.fields['numero'].initial is None):
                            if Telefone.objects.filter(pk=form_telefones.fields['id'].initial).exists():
                                Telefone.objects.get(pk=form_telefones.fields['id'].initial).delete()
                                if form.prefix not in resposta['fones']:
                                    resposta['fones'][form.prefix] = ''
                                resposta['fones'][form.prefix] += _(u'<p>O telefone %(type)s %(number)s foi excluído da base de dados</p>') % dict(
                                    type=form_telefones.instance.get_tipo_display(),
                                    number=form_telefones.instance.numero)
                        else:
                            for key, value in form_telefones.errors.iteritems():
                                key = form_telefones.prefix + "-id-errors"
                                resposta['erros'][key] = value

        json = simplejson.dumps(resposta)
        return HttpResponse(json, content_type='application/json')
    else:
        forms = [FuncionariosMobileForm(prefix=f.setor, instance=f)
                 for f, c in funcionarios]

    context = RequestContext(request, {'forms': forms,
                                       'diagnostico': diagnostico, 'casa_legislativa': casa_legislativa})
    return render_to_response('diagnosticos/diagnosticos_categoria_contatos_form.html',
                              context)

@login_required
def diagnostico_pdf(request, id_diagnostico):
    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    categorias = Categoria.objects.all()

    casa_legislativa = diagnostico.casa_legislativa
    funcionarios = []
    for n, l in Funcionario.SETOR_CHOICES:
        if casa_legislativa.funcionario_set.filter(setor=n).count() <= 1:
            funcionarios.append(casa_legislativa.funcionario_set.get_or_create(setor=n))
        else:
            for f in casa_legislativa.funcionario_set.filter(setor=n):
                funcionarios.append(f)

    schemas_by_categoria = []
    for categoria in categorias:
        schemas = []
        for schema in diagnostico.get_schemata(categoria.id):
            datatype = schema.datatype
            data = getattr(diagnostico, schema.name)
            if datatype == schema.TYPE_MANY:
                schema.value = [x.pk for x in data]
            elif datatype == schema.TYPE_ONE:
                schema.value = data.pk if data else None,
            else:
                schema.value = data
            schemas.append(schema)

        schemas_by_categoria.append((categoria, schemas))

    context = RequestContext(request, {
        'pagesize': 'A4',
        'casa_legislativa': casa_legislativa,
        'funcionarios': funcionarios,
        'diagnostico': diagnostico,
        'schemas_by_categoria': schemas_by_categoria,
    })

    return render_to_pdf('diagnosticos/diagnostico_pdf.html', context)
    # return render_to_response('diagnosticos/diagnostico_pdf.html', context)

@login_required
def graficos(request):
    categorias = Categoria.objects.all()

    sel_categoria = int(request.GET.get("categoria", "3"))
    perguntas = Pergunta.objects.filter(categoria=sel_categoria).all()

    context = RequestContext(request, {
        'categorias': categorias,
        'sel_categoria': sel_categoria,
        'perguntas': perguntas,
    })
    return render_to_response('diagnosticos/graficos.html',
                              context)


def percentage(fraction, population):
    try:
        return "%.0f%%" % ((float(fraction) / float(population)) * 100)
    except ValueError:
        return ''

@login_required
def grafico_api(request):

    colors = cycle(['#7cb5ec',
                    '#434348',
                    '#90ed7d',
                    '#f7a35c',
                    '#8085e9',
                    '#f15c80',
                    '#e4d354',
                    '#8085e8',
                    '#8d4653',
                    '#91e8e1', ])

    highlights = cycle(['#B0D3F4',
                        '#8E8E91',
                        '#BCF4B1',
                        '#FAC89D',
                        '#B3B6F2',
                        '#F79DB3',
                        '#EFE598',
                        '#B3B6F1',
                        '#BB9098',
                        '#BDF1ED', ])

    pergunta_slug = request.GET.get('id', None)
    pergunta = get_object_or_404(Pergunta, name=pergunta_slug)

    if pergunta.datatype == 'one':

        list_perguntas = pergunta.group_choices()
        list_perguntas = [{'label': k.title,
                           'value': v,
                           'color': colors.next(),
                           'highlight': highlights.next()}
                          for k, v in list_perguntas]

        # list_perguntas = [[k.title, v, colors.next(), highlights.next()] for k, v in list_perguntas]

    # elif pergunta.datatype == 'many':

    jsonn = simplejson.dumps(list_perguntas, sort_keys=True, indent=4, separators=(',', ': '))
    return HttpResponse(jsonn, content_type="application/json")

@login_required
def municipios_diagnosticados(self):
    municipios = []

    for d in Diagnostico.objects.all():
        m = d.casa_legislativa.municipio
        municipio = {'nome': d.casa_legislativa.nome + ', ' + m.uf.sigla, 'lat': str(m.latitude), 'lng': str(m.longitude), 'inicio': d.data_visita_inicio,
                     'fim': d.data_visita_fim, 'equipe': "<ul><li>" + "</li><li>".join([m.user.get_full_name() for m in d.membros]) + "</li></ul>", }
        municipios.append(municipio)

    return HttpResponse(simplejson.dumps(municipios), content_type='application/json')
