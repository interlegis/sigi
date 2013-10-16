# -*- coding: utf-8 -*-
from django import forms
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from sigi.apps.servicos.models import TipoServico, CasaAtendida, CasaManifesta, ServicoManifesto 
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.casas.models import CasaLegislativa
from django.template.context import RequestContext
from django.utils.encoding import force_unicode
from django.forms.forms import BoundField
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.contrib.admin.helpers import AdminForm

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
                         'servicos': "<ul><li>" + "</li><li>".join([s.tipo_servico.nome for s in casa.servico_set.filter(query)]) + "</li></ul>",}
            municipios.append(municipio)

    return HttpResponse(simplejson.dumps(municipios), mimetype="application/json")

class CasaManifestaProtoForm(forms.Form):
    fieldsets = None
    informante = forms.CharField(max_length=100, required=False)
    cargo = forms.CharField(max_length=100, required=False)
    
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
        fieldsets = ((None, ('informante', 'cargo'),),)
        
        for ts in TipoServico.objects.all():
            campos['possui_%s' % ts.pk] = forms.BooleanField(label='Possui o serviço de %s' % ts.nome, required=False)
            campos['url_%s' % ts.pk] = forms.URLField(label='Informe a URL', required=False)
            campos['hospedagem_interlegis_%s' % ts.pk] = forms.BooleanField(label=u'Serviço está hospedado no Interlegis', required=False)
            fieldsets += ((ts.nome, ('possui_%s' % ts.pk, 'url_%s' % ts.pk, 'hospedagem_interlegis_%s' % ts.pk )),)
            
        CasaManifestaForm = type('', (CasaManifestaProtoForm,), campos)
        
        if request.method == 'POST':
            cmf = CasaManifestaForm(request.POST)
            if cmf.is_valid():
                thanks = []
                cm, created = CasaManifesta.objects.get_or_create(casa_legislativa=casa)
                cm.informante = cmf.cleaned_data['informante']
                cm.cargo = cmf.cleaned_data['cargo']
                cm.save()
                thanks.append(('Informante', cmf.cleaned_data['informante']))
                thanks.append(('Cargo', cmf.cleaned_data['cargo']))
                for ts in TipoServico.objects.all():
                    if cmf.cleaned_data['possui_%s' % ts.pk]:
                        sm, created = ServicoManifesto.objects.get_or_create(casa_manifesta=cm, servico=ts)
                        sm.url = cmf.cleaned_data['url_%s' % ts.pk]
                        sm.hospedagem_interlegis = cmf.cleaned_data['hospedagem_interlegis_%s' % ts.pk]
                        sm.save()
                        thanks.append((ts.nome, 'Possui o serviço acessível em %s %s' % (sm.url, 'hospedado no Interlegis' if
                                                                                         sm.hospedagem_interlegis else '')))
                    else:
                        ServicoManifesto.objects.filter(casa_manifesta=cm, servico=ts).delete()
                        thanks.append((ts.nome, 'Não possui'))
                extra_context = {'casa': casa, 'thanks': thanks}
            else:
                extra_context = {'casa': casa, 'cmf': cmf}
        else:
            try:
                cm = casa.casamanifesta
                values = {
                    'informante': cm.informante,
                    'cargo': cm.cargo,
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
        
    # Monta formulário dinâmico dos serviços
#    campos = {}
#    for ts in TipoServico.objects.all():
#        campos['possui_%s' % ts.pk] = forms.BooleanField(label=ts.nome)
#        campos['url_%s' % ts.pk] = forms.URLField(label='URL do %s' % ts.nome)
#        campos['hospedagem_interlegis_%s' % ts.pk] = forms.BooleanField(label=u'Hospedado no Interlegis')
#    ServicoManifestoForm = type('', (forms.Form,), campos)
#    
#    if request.method == 'POST':
#        cm_form = CasaManifestaForm(request.POST)
#        sm_form = ServicoManifestoForm(request.POST)
#        
#        if cm_form.is_valid() and sm_form.is_valid():
#            return render_to_response('servicos/casa_manifesta.html', {'cm_form': cm_form, 'sm_form': sm_form},
#                                      context_instance=RequestContext(request))
#    else:
#        cm_form = CasaManifestaForm()
#        sm_form = ServicoManifestoForm()
    return render_to_response('casa_manifesta.html', {'cm_form': cm_form, 'sm_form': sm_form})