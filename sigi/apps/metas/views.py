# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.views.decorators.cache import cache_page
from sigi.apps.servicos.models import TipoServico, Servico
from sigi.apps.convenios.models import Projeto, Convenio
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.utils import to_ascii

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
    equipadas    = [] #[p.sigla for p in projeto_choices]
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


@cache_page(86400) # Cache de um dia (24 horas = 86400 segundos)
def map_data(request):
    """
    Monta json com todos os dados dos municípios que têm relação com o Interlegis
    """    

    casas = {}
    
    for c in CasaLegislativa.objects.select_related('servico', 'convenio', 'diagnostico').all().distinct():
        if c.servico_set.count() == 0 and c.convenio_set.count() == 0 and c.diagnostico_set.count() == 0:
            continue; # Salta essa casa, pois ela não tem nada com o Interlegis
        
        if not casas.has_key(c.pk):
            casa = {
                'nome': c.nome + ', ' + c.municipio.uf.sigla,
                'icone': 'mapmarker',
                'lat': str(c.municipio.latitude),
                'lng': str(c.municipio.longitude),
                'estado': c.municipio.uf.sigla,
                'regiao': c.municipio.uf.regiao,
                'diagnosticos': [], 
                'seit': [],
                'convenios': [],
                'equipadas': [],
                'info': []
            }
            
            for sv in c.servico_set.all():
                casa['info'].append(u"%s ativado em %s <a href='//%s' target='_blank'><img src='/sigi/media/images/link.gif' alt='link'></a>" % (sv.tipo_servico.nome, sv.data_ativacao.strftime('%d/%m/%Y'), sv.url))
                casa['seit'].append(sv.tipo_servico.sigla)
                
            for cv in c.convenio_set.all():
                if (cv.data_retorno_assinatura is None) and (cv.equipada and cv.data_termo_aceite.strftime('%d/%m/%Y') is not None):
                    casa['info'].append(u"Equipada em %s pelo %s" % (cv.data_termo_aceite.strftime('%d/%m/%Y'), cv.projeto.sigla))
                    casa['equipadas'].append(cv.projeto.sigla)
                if (cv.data_retorno_assinatura is not None) and not (cv.equipada and cv.data_termo_aceite.strftime('%d/%m/%Y') is not None):
                    casa['info'].append(u"Conveniada ao %s em %s" % (cv.projeto.sigla, cv.data_retorno_assinatura.strftime('%d/%m/%Y')))
                    casa['convenios'].append(cv.projeto.sigla)
                if (cv.data_retorno_assinatura is not None) and (cv.equipada and cv.data_termo_aceite.strftime('%d/%m/%Y') is not None):
                    casa['info'].append(u"Conveniada ao %s em %s e equipada em %s" % (cv.projeto.sigla, cv.data_retorno_assinatura.strftime('%d/%m/%Y'), cv.data_termo_aceite.strftime('%d/%m/%Y')))
                    casa['equipadas'].append(cv.projeto.sigla)
                    casa['convenios'].append(cv.projeto.sigla)
                    
            for dg in c.diagnostico_set.all():
                casa['diagnosticos'].append('P' if dg.publicado else 'A')
                casa['info'].append(u'Diagnosticada no período de %s a %s' % (dg.data_visita_inicio.strftime('%d/%m/%Y'), dg.data_visita_fim.strftime('%d/%m/%Y')))
                    
            casa['info'] = "<br/>".join(casa['info'])
                
            casas[c.pk] = casa
                
    return HttpResponse(simplejson.dumps(casas), mimetype="application/json")

def map_search(request):
    response = {'result': 'NOT_FOUND'}
    if 'q' in request.GET:
        q = request.GET.get('q')
        if len(q.split(',')) > 1:
            municipio, uf = [s.strip() for s in q.split(',')]
            casas = CasaLegislativa.objects.filter(search_text__icontains=to_ascii(municipio), municipio__uf__sigla__iexact=uf)
        else:
            casas = CasaLegislativa.objects.filter(search_text__icontains=to_ascii(q))
        if casas.count() > 0:
            response = {'result': 'FOUND', 'ids': [c.pk for c in casas]}
    
    return HttpResponse(simplejson.dumps(response), mimetype="application/json")