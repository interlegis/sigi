# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.views.decorators.cache import cache_page
from sigi.shortcuts import render_to_pdf
from sigi.apps.servicos.models import TipoServico, Servico
from sigi.apps.convenios.models import Projeto, Convenio
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.utils import to_ascii

from sigi.settings import MEDIA_ROOT
JSON_FILE_NAME = MEDIA_ROOT + 'map_data.json'

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


@cache_page(1800) # Cache de 30min
def map_data(request):
    """
    Retorna json com todos os dados dos municípios que têm relação com o Interlegis
    Tenta ler esse json do arquivo JSON_FILE_NAME. Se não encontrar, chama a rotina
    gera_map_data_file().
    """
    
    try:
        file = open(JSON_FILE_NAME, 'r')
        json = file.read()
    except:
        json = gera_map_data_file()
        
    return HttpResponse(json, mimetype="application/json")

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

@cache_page(86400) # Cache de um dia (24 horas = 86400 segundos)
def map_sum(request):
    # Filtrar Casas de acordo com os parâmetros
    param = get_params(request)
    casas = filtrar_casas(**param)
    
    # Montar registros de totalização
    tot_servicos = SortedDict()
    tot_projetos = SortedDict()
    tot_diagnosticos = SortedDict()

    for ts in TipoServico.objects.all():
        tot_servicos[ts.sigla] = 0

    for pr in Projeto.objects.all():
        tot_projetos[pr.sigla] = 0 

    tot_convenios = tot_projetos.copy()
    tot_equipadas = tot_projetos.copy() 

    tot_diagnosticos['A'] = 0
    tot_diagnosticos['P'] = 0
    
    # Montar as linhas do array de resultados com as regiões e os estados
    result = {}
    
    for uf in UnidadeFederativa.objects.filter(Q(regiao__in=param['regioes']) | Q(sigla__in=param['estados'])).order_by('regiao', 'nome'):
        if not result.has_key(uf.regiao):
            result[uf.regiao] = {'nome': uf.get_regiao_display(), 'ufs': {}, 'servicos': tot_servicos.copy(),
                                 'convenios': tot_projetos.copy(), 'equipadas': tot_projetos.copy(),
                                 'diagnosticos': tot_diagnosticos.copy()}
        result[uf.regiao]['ufs'][uf.codigo_ibge] = {'nome': uf.nome, 'servicos': tot_servicos.copy(),
                                                    'convenios': tot_projetos.copy(), 'equipadas': tot_projetos.copy(),
                                                    'diagnosticos': tot_diagnosticos.copy()}

    
    # Processar as casas filtradas
    for casa in casas.distinct():
        uf = casa.municipio.uf
        for s in casa.servico_set.all():
            tot_servicos[s.tipo_servico.sigla] += 1
            result[uf.regiao]['servicos'][s.tipo_servico.sigla] += 1
            result[uf.regiao]['ufs'][uf.codigo_ibge]['servicos'][s.tipo_servico.sigla] += 1
        for c in casa.convenio_set.all():
            tot_convenios[c.projeto.sigla] += 1
            result[uf.regiao]['convenios'][c.projeto.sigla] += 1
            result[uf.regiao]['ufs'][uf.codigo_ibge]['convenios'][c.projeto.sigla] += 1
            if (c.equipada and c.data_termo_aceite is not None):
                tot_equipadas[c.projeto.sigla] += 1
                result[uf.regiao]['equipadas'][c.projeto.sigla] += 1
                result[uf.regiao]['ufs'][uf.codigo_ibge]['equipadas'][c.projeto.sigla] += 1
        for d in casa.diagnostico_set.all():
            if d.publicado:
                tot_diagnosticos['P'] += 1
                result[uf.regiao]['diagnosticos']['P'] += 1
                result[uf.regiao]['ufs'][uf.codigo_ibge]['diagnosticos']['P'] += 1
            else:
                tot_diagnosticos['A'] += 1
                result[uf.regiao]['diagnosticos']['A'] += 1
                result[uf.regiao]['ufs'][uf.codigo_ibge]['diagnosticos']['A'] += 1
            
    extra_context = {
        'pagesize': 'a4 landscape',
        'servicos': TipoServico.objects.all(),
        'projetos': Projeto.objects.all(),
        'result': result,
        'tot_servicos': tot_servicos,
        'tot_convenios': tot_convenios,
        'tot_equipadas': tot_equipadas,
        'tot_diagnosticos': tot_diagnosticos,
    }        
    return render_to_pdf('metas/map_sum.html', extra_context)

def map_list(request):
    # Filtrar Casas de acordo com os parâmetros
    param = get_params(request)
    casas = filtrar_casas(**param)
    casas = casas.order_by('municipio__uf__regiao', 'municipio__uf__nome', 'nome').distinct()
    return render_to_pdf('metas/map_list.html', {'casas': casas})

#----------------------------------------------------------------------------------------------------
# Funções auxiliares - não são views
#---------------------------------------------------------------------------------------------------- 

def get_params(request):
    ''' Pegar parâmetros da pesquisa '''
    return {
        'seit'         : request.GET.getlist('seit'),
        'convenios'    : request.GET.getlist('convenios'),
        'equipadas'    : request.GET.getlist('equipadas'),
        'diagnosticos' : request.GET.getlist('diagnosticos'), 
        'regioes'      : request.GET.getlist('regioes'),
        'estados'      : request.GET.getlist('estados'),
    }

def filtrar_casas(seit, convenios, equipadas, regioes, estados, diagnosticos):
    ''' Filtrar Casas que atendem aos parâmetros de pesquisa '''
    qServico  = Q(servico__tipo_servico__sigla__in=seit)
    qConvenio = Q(convenio__projeto__sigla__in=convenios)
    qEquipada = Q(convenio__projeto__sigla__in=equipadas, convenio__equipada=True)
    qRegiao   = Q(municipio__uf__regiao__in=regioes)
    qEstado   = Q(municipio__uf__sigla__in=estados)
    
    if diagnosticos:
        qDiagnostico = Q(diagnostico__publicado__in=[p == 'P' for p in diagnosticos])
    else:
        qDiagnostico = Q()
        
    casas = CasaLegislativa.objects.filter(qServico | qConvenio | qEquipada | qDiagnostico).filter(qRegiao | qEstado)
    
    return casas

def gera_map_data_file(get_error=False):
    ''' Criar um arquivo json em settings.MEDIA_ROOT com o nome de map_data.json
        Este arquivo será consumido pela view de dados de mapa.
        Retorna os dados json.
        Caso get_error seja True e ocorra algum erro na gravação do arquivo,
        retorna a mensagem do erro que impediu a gravação. 
    ''' 
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
    
    json_data = simplejson.dumps(casas)
    
    try:
        file = open(JSON_FILE_NAME, 'w')
        file.write(json_data)
        file.close()
    except: # A gravação não foi bem sucedida ...
        if get_error: # ... o chamador deseja a mensagem de erro
            import sys
            return sys.exc_info()[0]
        else:
            pass # ... ou os dados poderão ser usados de qualquer forma
                
    return json_data