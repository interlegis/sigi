# -*- coding: utf-8 -*-
#
# sigi.apps.home.views
#
# Copyright (c) 2016 by Interlegis
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import calendar
import csv
import datetime
from itertools import cycle

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.convenios.models import Convenio, Projeto
from sigi.apps.diagnosticos.models import Diagnostico
from sigi.apps.metas.models import Meta
from sigi.apps.servicos.models import TipoServico
from sigi.apps.servidores.models import Servidor
from sigi.shortcuts import render_to_pdf


@never_cache
@login_required
def index(request):
    context = {'gerentes': Servidor.objects.exclude(casas_que_gerencia=None)}
    return render(request, 'index.html', context)

@never_cache
@login_required
def resumo_convenios(request):
    context = {'tabela_resumo_camara': busca_informacoes_camara() }
    return render(request, 'snippets/modules/resumo_convenios.html', context)

@never_cache
@login_required
def resumo_seit(request):
    mes = request.GET.get('mes', None)
    ano = request.GET.get('ano', None)
    
    try:
        mes = datetime.date(year=int(ano), month=int(mes), day=1)
        tabela_resumo_seit = busca_informacoes_seit(mes)
    except:
        tabela_resumo_seit = busca_informacoes_seit()

    context = {'tabela_resumo_seit': tabela_resumo_seit}
    return render(request, 'snippets/modules/resumo_seit.html', context)

@never_cache
@login_required
def chart_seit(request):
    mes = request.GET.get('mes', None)
    ano = request.GET.get('ano', None)
    
    try:
        mes = datetime.date(year=int(ano), month=int(mes), day=1)
        tabela_resumo_seit = busca_informacoes_seit(mes)
    except:
        tabela_resumo_seit = busca_informacoes_seit()
        
    data = {
        'type': 'line',
        'prevlink': reverse('home_chartseit') + ('?ano=%s&mes=%s' %
                        (tabela_resumo_seit['mes_anterior'].year,
                         tabela_resumo_seit['mes_anterior'].month)), 
        'nextlink': reverse('home_chartseit') + ('?ano=%s&mes=%s' %
                        (tabela_resumo_seit['proximo_mes'].year,
                         tabela_resumo_seit['proximo_mes'].month)), 
        'options': {'bezierCurve': False, 'datasetFill': False, 'pointDot': False, 'responsive': True},
        'data': {
            'labels': ['%02d/%s' % (mes.month, mes.year) for mes in reversed(tabela_resumo_seit['meses'])],
            'datasets': [
                {
                 'label': servico['nome'],
                 'strokeColor': servico['cor'],
                 'data': [mes['total'] for mes in reversed(servico['novos_por_mes'])]
                }
            for servico in tabela_resumo_seit['servicos']],
        }
    }
        
    return JsonResponse(data)

@never_cache
@login_required
def chart_convenios(request):
    q = request.GET.get('q', 'all')
    convenios = Convenio.objects.all()
    if q == 'assinados':
        convenios = convenios.exclude(data_retorno_assinatura=None)
    data = {
        'type': 'pie',
        'options': {'responsive': False, 'maintainAspectRatio': False},
        'data': grafico_convenio_projeto(convenios),
    }
    return JsonResponse(data)

@never_cache
@login_required
def chart_carteira(request):
    colors, highlights = color_palete()
    data = {'type': 'pie',
            'options': {'responsive': True},
            'data': [{'value': r['total_casas'], 
                      'color': colors.next(),
                      'highlight': highlights.next(),
                      'label': Servidor.objects.get(pk=r['gerente_contas']).nome_completo
                     }
                    for r in CasaLegislativa.objects.all().values('gerente_contas').annotate(total_casas=Count('pk')).order_by('gerente_contas')
                    ]
    }
    
    return JsonResponse(data)

@never_cache
@login_required
def chart_performance(request):
    servidor = request.GET.get('servidor', None)

    if servidor is None:
        casas = CasaLegislativa.objects.exclude(gerente_contas=None)
    else:
        gerente = get_object_or_404(Servidor, pk=servidor)
        casas = gerente.casas_que_gerencia
    
    data = {
        'type': 'pie',
        'options': {'responsive': True},
        'data': [
            {'label': _(u"Utilizam serviços"), 'value': casas.exclude(servico=None).count(), 'color': '#91e8e1'},
            {'label': _(u"Não utilizam serviços"), 'value': casas.filter(servico=None).count(), 'color': '#f7a35c'},
        ]
    }

    return JsonResponse(data)

@never_cache
@login_required
def report_sem_convenio(request):
    modo = request.GET.get('modo', None)
    format = request.GET.get('f', 'pdf')

    sc = sem_convenio()

    if modo == 'H':
        casas = sc['hospedagem']
        titulo = _(u"Casas sem convenio que utilizam algum serviço de hospedagem")
    elif modo == 'R':
        casas = sc['registro']
        titulo = _(u"Casas sem convenio que utilizam somente serviço de registro")
    else:
        casas = sc['total']
        titulo = _(u"Casas sem convenio que utilizam algum serviço de registro e/ou hospedagem")
        
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=casas.csv'
        writer = csv.writer(response)
        writer.writerow([titulo.encode('utf8')])
        writer.writerow([u''])
        writer.writerow([u'casa', u'uf', u'gerente', u'serviços'.encode('utf8')])
        for casa in casas:
            writer.writerow([
                casa.nome.encode('utf8'),
                casa.municipio.uf.sigla.encode('utf8'),
                casa.gerente_contas.nome_completo.encode('utf8'),
                (u', '.join(casa.servico_set.filter(data_desativacao__isnull=True).values_list('tipo_servico__nome', flat=True))).encode('utf8'),
            ])
        return response
    elif format == 'json':
        data = {
            'titulo': titulo,
            'casas': [
                {'nome': casa.nome,
                 'uf': casa.municipio.uf.sigla,
                 'gerente': casa.gerente_contas.nome_completo,
                 'servicos': list(casa.servico_set.filter(data_desativacao__isnull=True).values_list('tipo_servico__nome', flat=True))}
                for casa in casas
            ]
        }
        return JsonResponse(data, safe=False)
    else:
        context = {'casas': casas, 'titulo': titulo}
        return render_to_pdf('home/sem_convenio.html', context)
    
         
def busca_informacoes_camara():
    """
    Busca informacoes no banco para montar tabela de resumo de camaras por projeto
    Retorna um dicionario de listas
    """
    camaras = CasaLegislativa.objects.filter(tipo__sigla='CM')
    convenios = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM')
    projetos = Projeto.objects.all()

    convenios_assinados = convenios.exclude(data_retorno_assinatura=None)
    convenios_em_andamento = convenios.filter(data_retorno_assinatura=None)

    convenios_sem_adesao = convenios.filter(data_adesao=None)
    convenios_com_adesao = convenios.exclude(data_adesao=None)

    convenios_com_aceite = convenios.exclude(data_termo_aceite=None)

    camaras_sem_processo = camaras.filter(convenio=None)

    # Criacao das listas para o resumo de camaras por projeto

    cabecalho_topo = ['', ]  # Cabecalho superior da tabela

    lista_total = []
    lista_nao_aderidas = []
    lista_aderidas = []
    lista_convenios_assinados = []
    lista_convenios_em_andamento = []
    lista_camaras_equipadas = []
    for projeto in projetos:
        conv_sem_adesao_proj = convenios_sem_adesao.filter(projeto=projeto)
        conv_com_adesao_proj = convenios_com_adesao.filter(projeto=projeto)
        conv_assinados_proj = convenios_assinados.filter(projeto=projeto)
        conv_em_andamento_proj = convenios_em_andamento.filter(projeto=projeto)
        conv_equipadas_proj = convenios_com_aceite.filter(projeto=projeto)

        cabecalho_topo.append(projeto.sigla)
        lista_total.append(camaras.filter(convenio__projeto=projeto).count())
        lista_nao_aderidas.append(camaras.filter(convenio__in=conv_sem_adesao_proj).count())
        lista_aderidas.append(camaras.filter(convenio__in=conv_com_adesao_proj).count())
        lista_convenios_assinados.append(camaras.filter(convenio__in=conv_assinados_proj).count())
        lista_convenios_em_andamento.append(camaras.filter(convenio__in=conv_em_andamento_proj).count())
        lista_camaras_equipadas.append(camaras.filter(convenio__in=conv_equipadas_proj).count())

    # Monta linhas de diagnosticos
    lista_diagnosticos_digitados = ['', '', Diagnostico.objects.count(), '', '', '']
    lista_diagnosticos_publicados = ['', '', Diagnostico.objects.filter(publicado=True).count(), '', '', '']

    # Cabecalho da esquerda na tabela
    cabecalho_esquerda = (
        _(u'Câmaras municipais'),
        _(u'Câmaras municipais não aderidas'),
        _(u'Câmaras municipais aderidas'),
        _(u'Câmaras municipais com convênios assinados'),
        _(u'Câmaras municipais convênios em andamento'),
        _(u'Câmaras municipais equipadas'),
        _(u'Diagnósticos digitados'),
        _(u'Diagnósticos publicados')
    )

    linhas = (
        lista_total,
        lista_nao_aderidas,
        lista_aderidas,
        lista_convenios_assinados,
        lista_convenios_em_andamento,
        lista_camaras_equipadas,
        lista_diagnosticos_digitados,
        lista_diagnosticos_publicados
    )

    # Unindo as duas listass para que o cabecalho da esquerda fique junto com sua
    # respectiva linha
    lista_zip = zip(cabecalho_esquerda, linhas)
    
    # Retornando listas em forma de dicionario
    return {
        'cabecalho_topo': cabecalho_topo,
        'lista_zip': lista_zip,
        'total_camaras': camaras.count(),
        'camaras_sem_processo': camaras_sem_processo.count(),
        'sem_convenio': sem_convenio(),
    }


def sem_convenio():
    total = CasaLegislativa.objects.exclude(servico=None).filter(servico__data_desativacao=None, convenio=None).order_by('municipio__uf__sigla', 'nome').distinct('municipio__uf__sigla', 'nome')
    hospedagem = CasaLegislativa.objects.exclude(servico=None).filter(servico__data_desativacao=None, servico__tipo_servico__modo='H', convenio=None).order_by('municipio__uf__sigla', 'nome').distinct('municipio__uf__sigla', 'nome')
    reg_keys = set(total.values_list('pk', flat=True)).difference(set(hospedagem.values_list('pk', flat=True)))
    registro = CasaLegislativa.objects.filter(pk__in=reg_keys).order_by('municipio__uf__sigla', 'nome')
    return {
        'total': total,
        'hospedagem': hospedagem,
        'registro': registro,
    }

def grafico_convenio_projeto(convenios):
    colors, highlights = color_palete()
    projetos = Projeto.objects.all()
    lista_projetos = [{'label': projeto.sigla,
                       'value': convenios.filter(projeto=projeto).count(),
                       'color': colors.next(),
                       'highlight': highlights.next()}
                      for projeto in projetos]
    # remove projetos sem convenio
    lista_projetos = [x for x in lista_projetos if x['value'] > 0]

    # print lista_projetos
    # total_convenios = "Total: " + str(convenios.count())
    # lista_projetos.insert(0, total_convenios)
    return lista_projetos


def busca_informacoes_seit(mes_atual=None):
    colors, highlights = color_palete()
    if mes_atual is None:
        mes_atual = datetime.date.today().replace(day=1)
    mes_anterior = mes_atual - datetime.timedelta(days=1)
    proximo_mes = mes_atual + datetime.timedelta(days=calendar.monthrange(mes_atual.year, mes_atual.month)[1])
    
    meses = []
    mes = mes_atual
    for i in range(1, 13):
        meses.append(mes)
        mes = (mes - datetime.timedelta(days=1)).replace(day=1)
        
    result = {
        'mes_atual': mes_atual,
        'mes_anterior': mes_anterior,
        'proximo_mes': proximo_mes,
        'meses': meses,
        'titulos': [ '',
                     'Total de casas atendidas',
                     'Novas casas em %s/%s' % (mes_anterior.month, mes_anterior.year),
                     'Novas casas em %s/%s' % (mes_atual.month, mes_atual.year)
        ],
        'servicos': [],
    } 

    for tipo_servico in TipoServico.objects.all():
        por_mes = []
        for mes in meses:
            por_mes.append({'mes': '%02d/%s' % (mes.month, mes.year),
                            'total': tipo_servico.servico_set.filter(data_ativacao__year=mes.year, data_ativacao__month=mes.month).count()})

        result['servicos'].append(
            {'nome': tipo_servico.nome,
             'total': tipo_servico.servico_set.filter(Q(data_ativacao__lt=proximo_mes)&(Q(data_desativacao=None)|Q(data_desativacao__gt=proximo_mes))).count(),
             'novos_mes_anterior': tipo_servico.servico_set.filter(data_ativacao__year=mes_anterior.year, data_ativacao__month=mes_anterior.month).count(),
             'novos_mes_atual': tipo_servico.servico_set.filter(data_ativacao__year=mes_atual.year, data_ativacao__month=mes_atual.month).count(),
             'novos_por_mes': por_mes,
             'cor': colors.next(), 
             }
        )

    return result


def busca_informacoes_diagnostico():
    return [
        {'title': _(u'Diagnósticos digitados'), 'count': Diagnostico.objects.count()},
        {'title': _(u'Diagnósticos publicados'), 'count': Diagnostico.objects.filter(publicado=True).count()},
    ]


def color_palete():
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
    
    return (colors, highlights)
