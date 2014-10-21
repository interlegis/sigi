# -*- coding: utf-8 -*-
import csv
import os

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import json as simplejson  # XXX trocar isso por simplesmente import json e refatorar o codigo
from django.utils.datastructures import SortedDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.db.models.aggregates import Sum
from django.contrib.auth.decorators import user_passes_test, login_required
from sigi.settings import MEDIA_ROOT, STATIC_URL
from sigi.shortcuts import render_to_pdf
from sigi.apps.servicos.models import TipoServico, Servico
from sigi.apps.convenios.models import Projeto, Convenio
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.utils import to_ascii
from sigi.apps.financeiro.models import Desembolso
from sigi.apps.metas.templatetags.mapa_tags import descricao_servicos
from functools import reduce
from easy_thumbnails.templatetags.thumbnail import thumbnail_url
import time

JSON_FILE_NAME = os.path.join(MEDIA_ROOT, 'apps/metas/map_data.json')


@login_required
def dashboard(request):
    if request.user.groups.filter(name__in=['SPDT-Servidores', 'SSPLF']).count() <= 0:
        raise PermissionDenied

    desembolsos_max = 0
    matriz = SortedDict()
    dados = SortedDict()
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

    regiao_choices = UnidadeFederativa.REGIAO_CHOICES
    estado_choices = UnidadeFederativa.objects.all()
    servico_choices = TipoServico.objects.all()
    projeto_choices = Projeto.objects.all()

    seit = [ts.sigla for ts in servico_choices]
    convenios = ['PML']  # Apenas o ultimo #hardcoded #fixme
    equipadas = []  # [p.sigla for p in projeto_choices]
    diagnosticos = ['P']  # choices: ["A", "P"]
    regioes = [r[0] for r in regiao_choices]
    estados = []

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

        srv = {}
        for ts in TipoServico.objects.all():
            srv[ts.pk] = ts.nome

        cnv = {}
        for pr in Projeto.objects.all():
            cnv[pr.id] = pr.sigla

        writer.writerow([u'codigo_ibge', u'nome_casa', u'municipio', u'uf', u'regiao', ] + [x for x in srv.values()] +
                        reduce(lambda x, y: x + y, [['conveniada ao %s' % x, 'equipada por %s' % x] for x in cnv.values()]))

        for casa in casas:
            row = [casa.municipio.codigo_ibge, casa.nome, casa.municipio.nome, casa.municipio.uf.sigla,
                   casa.municipio.uf.get_regiao_display(), ]
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
    }


def filtrar_casas(seit, convenios, equipadas, regioes, estados, diagnosticos):
    ''' Filtrar Casas que atendem aos parâmetros de pesquisa '''
    qServico = Q(servico__tipo_servico__sigla__in=seit)
    qConvenio = Q(convenio__projeto__sigla__in=convenios)
    qEquipada = Q(convenio__projeto__sigla__in=equipadas, convenio__equipada=True)
    qRegiao = Q(municipio__uf__regiao__in=regioes)
    qEstado = Q(municipio__uf__sigla__in=estados)

    if diagnosticos:
        qDiagnostico = Q(diagnostico__publicado__in=[p == 'P' for p in diagnosticos])
    else:
        qDiagnostico = Q()

    casas = CasaLegislativa.objects.filter(qServico | qConvenio | qEquipada | qDiagnostico).filter(qRegiao | qEstado)

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

    for c in CasaLegislativa.objects.select_related('servico', 'convenio', 'diagnostico').all().distinct():
        if c.servico_set.count() == 0 and c.convenio_set.count() == 0 and c.diagnostico_set.count() == 0:
            continue
            # Salta essa casa, pois ela não tem nada com o Interlegis

        if c.pk not in casas:
            casa = {
                'nome': c.nome + ', ' + c.municipio.uf.sigla,
                'icone': '/static/img/mapmarker.png',
                'thumb': thumbnail_url(c.foto, 'small'),
                'foto': (c.foto.url if c.foto else ''),
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
                casa['info'].append(u"%s ativado em %s <a href='%s' target='_blank'><img src='%simg/link.gif' alt='link'></a>" % (
                    sv.tipo_servico.nome, sv.data_ativacao.strftime('%d/%m/%Y') if sv.data_ativacao else
                    u'<sem data de ativação>', sv.url, STATIC_URL))
                casa['seit'].append(sv.tipo_servico.sigla)

            for cv in c.convenio_set.all():
                if (cv.data_retorno_assinatura is None) and (cv.equipada and cv.data_termo_aceite is not None):
                    casa['info'].append(u"Equipada em %s pelo %s" % (cv.data_termo_aceite.strftime('%d/%m/%Y'), cv.projeto.sigla))
                    casa['equipadas'].append(cv.projeto.sigla)
                if (cv.data_retorno_assinatura is not None) and not (cv.equipada and cv.data_termo_aceite is not None):
                    casa['info'].append(u"Conveniada ao %s em %s" % (cv.projeto.sigla, cv.data_retorno_assinatura.strftime('%d/%m/%Y')))
                    casa['convenios'].append(cv.projeto.sigla)
                if (cv.data_retorno_assinatura is not None) and (cv.equipada and cv.data_termo_aceite is not None):
                    casa['info'].append(u"Conveniada ao %s em %s e equipada em %s" % (cv.projeto.sigla, cv.data_retorno_assinatura.strftime('%d/%m/%Y'), cv.data_termo_aceite.strftime('%d/%m/%Y')))
                    casa['equipadas'].append(cv.projeto.sigla)
                    casa['convenios'].append(cv.projeto.sigla)

            for dg in c.diagnostico_set.all():
                casa['diagnosticos'].append('P' if dg.publicado else 'A')
                casa['info'].append(u'Diagnosticada no período de %s a %s' % (dg.data_visita_inicio.strftime('%d/%m/%Y') if
                                                                              dg.data_visita_inicio is not None else u"<sem data de início>",
                                                                              dg.data_visita_fim.strftime('%d/%m/%Y') if dg.data_visita_fim else u"<sem data de término>"))

            casa['info'] = "<br/>".join(casa['info'])

            casas[c.pk] = casa

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
        return "Arquivo %s gerado em %d segundos" % (JSON_FILE_NAME, time.time() - start)

    return json_data
