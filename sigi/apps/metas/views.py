# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from sigi.apps.servicos.models import TipoServico, Servico
from sigi.apps.convenios.models import Projeto, Convenio
from sigi.apps.contatos.models import UnidadeFederativa
from apps.casas.models import CasaLegislativa

def mapa(request):
    """
    Mostra o mapa com filtros carregados com valores default
    """
    
    regiao_choices = UnidadeFederativa.REGIAO_CHOICES
    estado_choices = UnidadeFederativa.objects.all()
    servico_choices = TipoServico.objects.all()
    projeto_choices = Projeto.objects.all()
    
    seit         = [ ts.sigla for ts in servico_choices]
    convenios    = ['PML'] # Apenas o ultimo #hardcoded #fixme
    equipadas    = [p.sigla for p in projeto_choices]
    diagnosticos = ['P'] # choices: ["A", "P"] 
    regioes      = [r[0] for r in regiao_choices]
    estados      = []
    
    extra_context = {
        'seit': seit,
        'convenios': convenios,
        'equipadas': equipadas,
        'diagnosticos': diagnosticos,
        'regioes': regioes,
        'estados': estados,
        'regiao_choices': regiao_choices,
        'estado_choices': estado_choices,
        'servico_choices': servico_choices,
        'projeto_choices': projeto_choices,
    }
    
    return render_to_response('metas/mapa.html', extra_context, context_instance=RequestContext(request))

def map_data(request):
    """
    Monta json com dados dos municípios conforme seleção do usuário
    """
    
    # Seleções default
    regiao_choices = UnidadeFederativa.REGIAO_CHOICES
    
    seit         = request.POST.getlist('seit')
    convenios    = request.POST.getlist('convenios')
    equipadas    = request.POST.getlist('equipadas')
    diagnosticos = request.POST.getlist('diagnosticos')
    regioes      = request.POST.getlist('regioes')
    estados      = request.POST.getlist('estados')
    
    qRegiao       = Q(municipio__uf__regiao__in=regioes) if len(regioes) < len(regiao_choices) else Q()
    qEstado       = Q(municipio__uf__sigla__in=estados) if estados else Q()
    qSeit         = Q(servico__data_desativacao=None, servico__tipo_servico__sigla__in=seit) if seit else Q()
    qConvenios    = Q(~Q(convenio__data_retorno_assinatura=None), tipo__sigla='CM', convenio__projeto__sigla__in=convenios) if convenios else Q()
    qEquipadas    = Q(tipo__sigla='CM', convenio__equipada=True, convenio__projeto__sigla__in=equipadas) if equipadas else Q()
    qDiagnosticos = Q((Q(diagnostico__publicado=True) if 'P' in diagnosticos else Q()) | 
                      (Q(diagnostico__publicado=False) if 'A' in diagnosticos else Q())) 
    
    casas = {}
    
    for c in CasaLegislativa.objects.select_related('servico', 'convenio', 'diagnostico').filter(qRegiao | qEstado).filter(qSeit | 
                qConvenios | qEquipadas | qDiagnosticos).distinct():
        if not casas.has_key(c.pk):
            casa = {
                'nome': c.nome + ', ' + c.municipio.uf.sigla,
                'icone': 'mapmarker',
                'lat': str(c.municipio.latitude),
                'lng': str(c.municipio.longitude),
                'info': []
            }
            
            for sv in c.servico_set.all():
                casa['info'].append("%s ativado em %s" % (sv.tipo_servico.nome, sv.data_ativacao))
                
            for cv in c.convenio_set.all():
                if (cv.data_retorno_assinatura is None) and (cv.equipada and cv.data_termo_aceite is not None):
                    casa['info'].append("Equipada em %s pelo %s" % (cv.data_termo_aceite, cv.projeto.sigla))
                if (cv.data_retorno_assinatura is not None) and not (cv.equipada and cv.data_termo_aceite is not None):
                    casa['info'].append("Conveniada ao %s em %s" % (cv.projeto.sigla, cv.data_retorno_assinatura))
                if (cv.data_retorno_assinatura is not None) and (cv.equipada and cv.data_termo_aceite is not None):
                    casa['info'].append("Conveniada ao %s em %s e equipada em %s" % (cv.projeto.sigla, cv.data_retorno_assinatura, cv.data_termo_aceite))
                    
            for dg in c.diagnostico_set.all():
                casa['info'].append('Diagnosticada no período de %s a %s' % (dg.data_visita_inicio, dg.data_visita_fim))
                    
            casa['info'] = "<br/>".join(casa['info'])
                
            casas[c.pk] = casa
     
#-------------------------------------------------------------------------------------------------------------------------------
#    if seit:    
#        for srv in Servico.objects.filter(qRegiao, qEstado, data_desativacao=None, tipo_servico__sigla__in=seit):
#            if casas.has_key(srv.casa_legislativa.id):
#                casa = casas[srv.casa_legislativa.id]
#            else:
#                casa = {
#                    'nome': srv.casa_legislativa.nome + ', ' + srv.casa_legislativa.municipio.uf.sigla,
#                    'icon': 'mapmarker',
#                    'lat': str(srv.casa_legislativa.municipio.latitude),
#                    'lng': str(srv.casa_legislativa.municipio.longitude),
#                    'info': []
#                }
#                casas[srv.casa_legislativa.id] = casa
#    
#            casa['info'].append(srv.tipo_servico.nome)
#    
#    if convenios:
#        for cnv in Convenio.objects.filter(qRegiao, qEstado, casa_legislativa__tipo__sigla='CM', projeto__sigla__in=convenios) \
#                    .exclude(data_retorno_assinatura=None):
#            if casas.has_key(cnv.casa_legislativa.id):
#                casa = casas[cnv.casa_legislativa.id]
#            else:
#                casa = {
#                    'nome': cnv.casa_legislativa.nome + ', ' + cnv.casa_legislativa.municipio.uf.sigla,
#                    'icon': 'mapmarker',
#                    'lat': str(cnv.casa_legislativa.municipio.latitude),
#                    'lng': str(cnv.casa_legislativa.municipio.longitude),
#                    'info': []
#                }
#                casas[cnv.casa_legislativa.id] = casa
#    
#            casa['info'].append('Convênio %s assinado em %s' % (cnv.projeto.sigla, cnv.data_retorno_assinatura))
#    
#    if equipadas:    
#        for eqp in Convenio.objects.filter(qRegiao, qEstado, casa_legislativa__tipo__sigla='CM', equipada=True, projeto__sigla__in=equipadas)\
#                    .exclude(data_termo_aceite=None):
#            if casas.has_key(eqp.casa_legislativa.id):
#                casa = casas[eqp.casa_legislativa.id]
#            else:
#                casa = {
#                    'nome': eqp.casa_legislativa.nome + ', ' + eqp.casa_legislativa.municipio.uf.sigla,
#                    'icon': 'mapmarker',
#                    'lat': str(eqp.casa_legislativa.municipio.latitude),
#                    'lng': str(eqp.casa_legislativa.municipio.longitude),
#                    'info': []
#                }
#                casas[eqp.casa_legislativa.id] = casa
#    
#            casa['info'].append('Equipada pelo %s em %s' % (eqp.projeto.sigla, eqp.data_termo_aceite))
#-------------------------------------------------------------------------------------------------------------------------------
    
    return HttpResponse(simplejson.dumps(casas), mimetype="application/json")