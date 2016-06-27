# -*- coding: utf-8 -*-
import csv
import json as simplejson  # XXX trocar isso por simplesmente import json e refatorar o codigo
import os
import time
from collections import OrderedDict
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.convenios.models import Projeto
from sigi.apps.financeiro.models import Desembolso
from sigi.apps.servicos.models import TipoServico
from sigi.apps.utils import to_ascii
from sigi.settings import MEDIA_ROOT, STATIC_URL
from sigi.shortcuts import render_to_pdf

JSON_FILE_NAME = os.path.join(MEDIA_ROOT, 'apps/metas/map_data.json')


@login_required
def dashboard(request):
    if request.user.groups.filter(name__in=['SPDT-Servidores', 'SSPLF']).count() <= 0:
        raise PermissionDenied

    desembolsos_max = 0
    matriz = OrderedDict()
    dados = OrderedDict()
    projetos = Projeto.objects.all()
    meses = Desembolso.objects.dates('data', 'month', 'DESC')[:6]
    colors = ['ffff00', 'cc7900', 'ff0000', '92d050', '006600', '0097cc', '002776', 'ae78d6', 'ff00ff', '430080',
              '28d75c', '0000ff', 'fff200']

    for date in reversed(meses):
        mes_ano = '%s/%s' % (date.month, date.year)
        dados[mes_ano] = 0

    for p in projetos:
        matriz[p.id] = (p.sigla, dados.copy())

    for date in meses:
        mes_ano = '%s/%s' % (date.month, date.year)
        for d in Desembolso.objects.filter(data__year=date.year, data__month=date.month).values('projeto').annotate(total_dolar=Sum('valor_dolar')):
            if int(d['total_dolar']) > desembolsos_max:
                desembolsos_max = int(d['total_dolar'])
            matriz[d['projeto']][1][mes_ano] += int(d['total_dolar'])

    meses = ["%s/%s" % (m.month, m.year) for m in reversed(meses)]
    extra_context = {'desembolsos': matriz, 'desembolsos_max': desembolsos_max, 'meses': meses, 'colors': ','.join(colors[:len(matriz)])}
    return render_to_response('metas/dashboard.html', extra_context, context_instance=RequestContext(request))


def mapa(request):
    """
    Mostra o mapa com filtros carregados com valores default
    """

    projetos = Projeto.objects.all()
    filters = (
        # NAME, HEADING,
        #     [(value, label, checked) ...]
        ("seit", _(u'Por Serviços SEIT'),
            [(x.sigla, x.sigla, x.nome, True)
                for x in TipoServico.objects.all()]),
        ("convenios", _(u'Por Casas conveniadas'),
            [(x.sigla, 'convenio_' + x.sigla, _(u'ao %(projeto)s') % {'projeto': x.sigla}, x.sigla == 'PML')
                for x in projetos]),  # Apenas o ultimo #hardcoded #fixme
        ("equipadas", _(u'Por Casas equipadas'),
            [(x.sigla, 'equip_' + x.sigla, _(u'pelo %(projeto)s') % {'projeto': x.sigla}, False)
                for x in projetos]),
        ("diagnosticos", _(u'Por Diagnósticos'),
            [('A', 'diagnostico_A', 'Em andamento', False),
             ('P', 'diagnostico_P', 'Publicados', True)]),
        ("regioes", _(u'Por região'),
            [(x[0], x[0], x[1], True)
                for x in UnidadeFederativa.REGIAO_CHOICES]),
        ("estados", _(u'Por Estado'),
            [(x.sigla, x.sigla, x.nome, False)
                for x in UnidadeFederativa.objects.all()]),
        ("gerente", _(u'Por gerente de relacionamento'),
            [("", 'gerente_', _(u"Sem gerente"), False)] +
            [(x.gerente_contas.id, 'gerente_%s' % (x.gerente_contas.id,),
              "%s %s" % (x.gerente_contas.nome_completo.split()[0], x.gerente_contas.nome_completo.split()[-1]), False)
             for x in CasaLegislativa.objects.exclude(gerente_contas=None).select_related(
                        'gerente_contas').distinct('gerente_contas__nome_completo').order_by('gerente_contas__nome_completo')]),
    )
    return render(request, 'metas/mapa.html', {'filters': filters})


@cache_page(1800)  # Cache de 30min
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

    return HttpResponse(json, content_type='application/json')


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

    return HttpResponse(simplejson.dumps(response), content_type='application/json')


@cache_page(86400)  # Cache de um dia (24 horas = 86400 segundos)
def map_sum(request):
    # Filtrar Casas de acordo com os parâmetros
    param = get_params(request)
    casas = filtrar_casas(**param)

    # Montar registros de totalização
    tot_servicos = OrderedDict()
    tot_projetos = OrderedDict()
    tot_diagnosticos = OrderedDict()

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
        if uf.regiao not in result:
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


@cache_page(86400)  # Cache de um dia (24 horas = 86400 segundos)
def map_list(request):
    # Filtrar Casas de acordo com os parâmetros
    param = get_params(request)
    formato = request.GET.get('fmt', 'pdf')
    casas = filtrar_casas(**param)
    casas = casas.order_by('municipio__uf__regiao', 'municipio__uf__nome', 'nome').distinct()

    if formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="maplist.csv"'
        writer = csv.writer(response)

        srv = {x[0]: x[1] for x in TipoServico.objects.values_list('id', 'nome')}
        cnv = {x[0]: x[1] for x in Projeto.objects.values_list('id', 'sigla')}
        
        head = [s.encode('utf-8') for s in 
                [u'código IBGE', u'nome da casa', u'município', u'UF', u'região', ] +
                [x for x in srv.values()] +
                reduce(lambda x, y: x + y, 
                       [['conveniada ao %s' % x, 'equipada por %s' % x] for x in cnv.values()])]

        writer.writerow(head)

        for casa in casas:
            row = [casa.municipio.codigo_ibge,
                   casa.nome.encode('utf-8'),
                   casa.municipio.nome.encode('utf-8'),
                   casa.municipio.uf.sigla.encode('utf-8'),
                   casa.municipio.uf.get_regiao_display().encode('utf-8'), ]
            
            for id in srv.keys():
                try:
                    sv = casa.servico_set.get(tipo_servico__id=id)
                    row += [sv.data_ativacao, ]
                except:
                    row += [None, ]

            for id in cnv.keys():
                try:
                    cv = casa.convenio_set.get(projeto__id=id)
                    row += [cv.data_retorno_assinatura, cv.data_termo_aceite if cv.equipada else None, ]
                except:
                    row += [None, None, ]

            writer.writerow(row)
        return response

    return render_to_pdf('metas/map_list.html', {'casas': casas})


#----------------------------------------------------------------------------------------------------
# Funções auxiliares - não são views
#----------------------------------------------------------------------------------------------------

def get_params(request):
    ''' Pegar parâmetros da pesquisa '''
    return {
        'seit': request.GET.getlist('seit'),
        'convenios': request.GET.getlist('convenios'),
        'equipadas': request.GET.getlist('equipadas'),
        'diagnosticos': request.GET.getlist('diagnosticos'),
        'regioes': request.GET.getlist('regioes'),
        'estados': request.GET.getlist('estados'),
        'gerentes': request.GET.getlist('gerente'),
    }


def filtrar_casas(seit, convenios, equipadas, regioes, estados, diagnosticos, gerentes):
    ''' Filtrar Casas que atendem aos parâmetros de pesquisa '''

    qServico  = Q(servico__tipo_servico__sigla__in=seit)
    qConvenio = Q(convenio__projeto__sigla__in=convenios)
    qEquipada = Q(convenio__projeto__sigla__in=equipadas, convenio__equipada=True)
        
    qRegiao = Q(municipio__uf__regiao__in=regioes)
    qEstado = Q(municipio__uf__sigla__in=estados)
    
    if gerentes:
        qGerente = Q(gerente_contas_id__in=gerentes)
    else:
        qGerente = Q()

    if diagnosticos:
        qDiagnostico = Q(diagnostico__publicado__in=[p == 'P' for p in diagnosticos])
    else:
        qDiagnostico = Q()
        
    casas = CasaLegislativa.objects.filter(qRegiao | qEstado).filter(qGerente)
    
    if seit or convenios or equipadas or diagnosticos:
        casas = casas.filter(qServico | qConvenio | qEquipada | qDiagnostico)
    else:
        casas = casas.filter(Q(servico=None) & Q(convenio=None) & Q(diagnostico=None))

    return casas


def gera_map_data_file(cronjob=False):
    ''' Criar um arquivo json em {settings.MEDIA_ROOT}/apps/metas/ com o nome de map_data.json
        Este arquivo será consumido pela view de dados de mapa.
        Retorna os dados json caso cronjob seja falso.
        Caso cronjob seja True, retorna log de tempo gasto na geração ou a mensagem do erro
        que impediu a gravação do arquivo.
    '''
    start = time.time()

    casas = {}

    for c in CasaLegislativa.objects.prefetch_related('servico_set', 'convenio_set', 'diagnostico_set').all().distinct():
#         if c.servico_set.count() == 0 and c.convenio_set.count() == 0 and c.diagnostico_set.count() == 0:
#             continue
#             # Salta essa casa, pois ela não tem nada com o Interlegis

        if c.pk not in casas:
            summary = parliament_summary(c)
            summary['info'] = "<br/>".join(summary['info'])
            casas[c.pk] = summary

    json_data = simplejson.dumps(casas)

    try:
        file = open(JSON_FILE_NAME, 'w')
        file.write(json_data)
        file.close()
    except Exception as e:  # A gravação não foi bem sucedida ...
        if cronjob:  # ... o chamador deseja a mensagem de erro
            return str(e)
        else:
            pass  # ... ou os dados poderão ser usados de qualquer forma

    if cronjob:
        return _(u"Arquivo %(filename)s gerado em %(seconds)d segundos") % dict(
            filename=JSON_FILE_NAME,
            seconds=time.time() - start)

    return json_data


def parliament_summary(parliament):
    summary = {
        'nome': parliament.nome + ', ' + parliament.municipio.uf.sigla,
        'thumb': thumbnail_url(parliament.foto, 'small'),
        'foto': (parliament.foto.url if parliament.foto else ''),
        'lat': str(parliament.municipio.latitude),
        'lng': str(parliament.municipio.longitude),
        'estado': parliament.municipio.uf.sigla,
        'regiao': parliament.municipio.uf.regiao,
        'gerente': (str(parliament.gerente_contas.id) if parliament.gerente_contas else ''),
        'diagnosticos': [],
        'seit': [],
        'convenios': [],
        'equipadas': [],
        'info': []
    }
    
    if parliament.gerente_contas:
        summary['info'].append(_(u"Gerente de relacionamento: %s") % parliament.gerente_contas.nome_completo)

    for sv in parliament.servico_set.filter(data_desativacao=None):
        summary['info'].append(
            _(u"%(name)s ativado em %(date)s") % dict(
                name=sv.tipo_servico.nome,
                date=sv.data_ativacao.strftime('%d/%m/%Y') if sv.data_ativacao else _(u'<sem data de ativação>')) +
            " <a href='%s' target='_blank'><img src='%simg/link.gif' alt='link'></a>" % (sv.url, STATIC_URL))
        summary['seit'].append(sv.tipo_servico.sigla)

    for cv in parliament.convenio_set.all():
        if (cv.data_retorno_assinatura is None) and (cv.equipada and cv.data_termo_aceite is not None):
            summary['info'].append(_(u"Equipada em %(date)s pelo %(project)s") % dict(
                date=cv.data_termo_aceite.strftime('%d/%m/%Y'),
                project=cv.projeto.sigla))
            summary['equipadas'].append(cv.projeto.sigla)
        elif cv.data_retorno_assinatura is None:
            summary['info'].append(_(u"Adesão ao projeto %(project)s, em %(date)s") % dict(
                project=cv.projeto.sigla,
                date=cv.data_adesao))
            summary['convenios'].append(cv.projeto.sigla)
        if (cv.data_retorno_assinatura is not None) and not (cv.equipada and cv.data_termo_aceite is not None):
            summary['info'].append(_(u"Conveniada ao %(project)s em %(date)s") % dict(
                project=cv.projeto.sigla,
                date=cv.data_retorno_assinatura.strftime('%d/%m/%Y')))
            summary['convenios'].append(cv.projeto.sigla)
        if (cv.data_retorno_assinatura is not None) and (cv.equipada and cv.data_termo_aceite is not None):
            summary['info'].append(_(u"Conveniada ao %(project)s em %(date)s e equipada em %(equipped_date)s") % dict(
                project=cv.projeto.sigla,
                date=cv.data_retorno_assinatura.strftime('%d/%m/%Y'),
                equipped_date=cv.data_termo_aceite.strftime('%d/%m/%Y')))
            summary['equipadas'].append(cv.projeto.sigla)
            summary['convenios'].append(cv.projeto.sigla)

    for dg in parliament.diagnostico_set.all():
        summary['diagnosticos'].append('P' if dg.publicado else 'A')
        summary['info'].append(_(u'Diagnosticada no período de %(initial_date)s a %(final_date)s') % dict(
            initial_date=dg.data_visita_inicio.strftime('%d/%m/%Y') if dg.data_visita_inicio is not None else _(u"<sem data de início>"),
            final_date=dg.data_visita_fim.strftime('%d/%m/%Y') if dg.data_visita_fim else _(u"<sem data de término>")))

    return summary
