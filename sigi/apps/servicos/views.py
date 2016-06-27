# -*- coding: utf-8 -*-
import json as simplejson  # XXX trocar isso por simplesmente import json e refatorar o codigo

from django import forms
from django.db.models import Q
from django.forms.forms import BoundField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.servicos.models import (CasaAtendida, CasaManifesta,
                                       ServicoManifesto, TipoServico)


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
        casa = get_object_or_404(CasaLegislativa, pk=casa_id)

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
        extra_context = {'casa_list': CasaLegislativa.objects.filter(municipio__uf__sigla=uf)}
    else:
        extra_context = {'uf_list': UnidadeFederativa.objects.all()}

    return render_to_response('servicos/casa_manifesta.html', extra_context, context_instance=RequestContext(request))
