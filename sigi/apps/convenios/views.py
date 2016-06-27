#-*- coding:utf-8 -*-
import csv
import datetime

import ho.pisa as pisa
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, render
from django.template import Context, loader
from django.utils.translation import ugettext as _
from geraldo.generators import PDFGenerator

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.convenios.models import Convenio, Projeto
from sigi.apps.convenios.reports import (ConvenioPorALReport,
                                         ConvenioPorCMReport,
                                         ConvenioReportSemAceiteAL,
                                         ConvenioReportSemAceiteCM)


def query_ordena(qs, o, ot):
    list_display = ('num_convenio', 'casa_legislativa',
                    'data_adesao', 'data_retorno_assinatura', 'data_termo_aceite',
                    'projeto',
                    )

    aux = list_display[(int(o) - 1)]
    if ot == 'asc':
        qs = qs.order_by(aux)
    else:
        qs = qs.order_by("-" + aux)
    return qs


def get_for_qs(get, qs):
    kwargs = {}
    ids = 0
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
        qs = Convenio.objects.extra(where=[query])
    return qs


def carrinhoOrGet_for_qs(request):
    """
       Verifica se existe convênios na sessão se não verifica get e retorna qs correspondente.
    """
    if 'carrinho_convenios' in request.session:
        ids = request.session['carrinho_convenios']
        qs = Convenio.objects.filter(pk__in=ids)
    else:
        qs = Convenio.objects.all()
        if request.GET:
            qs = qs.order_by("casa_legislativa__municipio__uf", "casa_legislativa__municipio")
            qs = get_for_qs(request.GET, qs)
    return qs


def adicionar_convenios_carrinho(request, queryset=None, id=None):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
        if 'carrinho_convenios' not in request.session:
            request.session['carrinho_convenios'] = ids_selecionados
        else:
            lista = request.session['carrinho_convenios']
            # Verifica se id já não está adicionado
            for id in ids_selecionados:
                if id not in lista:
                    lista.append(id)
            request.session['carrinho_convenios'] = lista

@login_required
def excluir_carrinho(request):
    if 'carrinho_convenios' in request.session:
        del request.session['carrinho_convenios']
    return HttpResponseRedirect('.')

@login_required
def deleta_itens_carrinho(request):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
        if 'carrinho_convenios' in request.session:
            lista = request.session['carrinho_convenios']
            for item in ids_selecionados:
                lista.remove(item)
            if lista:
                request.session['carrinho_convenios'] = lista
            else:
                del lista
                del request.session['carrinho_convenios']

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

    carrinhoIsEmpty = not('carrinho_convenios' in request.session)

    return render(
        request,
        'convenios/carrinho.html',
        {
            'carIsEmpty': carrinhoIsEmpty,
            'paginas': paginas,
            'query_str': '?' + request.META['QUERY_STRING']
        }
    )

@login_required
def report(request, id=None):

    if id:
        qs = Convenio.objects.filter(pk=id)
    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    tipo = ''
    data_aceite_has = ''
    report = None
    if request.POST:
        if 'filtro_casa' in request.POST:
            tipo = request.POST['filtro_casa']
        if 'data_aceite' in request.POST:
            data_aceite_has = request.POST['data_aceite']
        # Verifica filtro se é por Assembleia
        if tipo == 'al':
            qs = qs.filter(casa_legislativa__tipo__sigla='AL')
            # Verifica se é com data de aceite
            if data_aceite_has == 'nao':
                report = ConvenioReportSemAceiteAL(queryset=qs)
            else:
                report = ConvenioPorALReport(queryset=qs)
        else:
            qs = qs.filter(casa_legislativa__tipo__sigla='CM')
            if data_aceite_has == 'nao':
                report = ConvenioReportSemAceiteCM(queryset=qs)
            else:
                report = ConvenioPorCMReport(queryset=qs)

    response = HttpResponse(content_type='application/pdf')
    if report:
        report.generate_by(PDFGenerator, filename=response)
    else:
        return HttpResponseRedirect('../')
    return response


def casas_estado_to_tabela(casas, convenios, regiao):

    estados = get_list_or_404(UnidadeFederativa, regiao=regiao)

    class LinhaEstado():
        pass

    lista = []

    for estado in estados:
        linha = LinhaEstado()

        convenios_est = convenios.filter(casa_legislativa__municipio__uf=estado)
        convenios_est_publicados = convenios_est.exclude(data_pub_diario=None)
        convenios_est_equipados = convenios_est.exclude(data_termo_aceite=None)

        casas_est = casas.filter(municipio__uf=estado)
        casas_est_nao_aderidas = casas_est.exclude(convenio__in=convenios_est).distinct()
        casas_est_aderidas = casas_est.filter(convenio__in=convenios_est).distinct()
        casas_est_conveniadas = casas_est.filter(convenio__in=convenios_est_publicados).distinct()
        casas_est_equipadas = casas_est.filter(convenio__in=convenios_est_equipados).distinct()

        linha.lista = (
            casas_est.count(),
            casas_est_nao_aderidas.count(),
            casas_est_aderidas.count(),
            casas_est_conveniadas.count(),
            casas_est_equipadas.count(),
        )

        linha.estado = estado

        lista.append(linha)

    casas_regiao = casas.filter(municipio__uf__regiao=regiao)
    convenios_regiao = convenios.filter(casa_legislativa__municipio__uf__regiao=regiao)
    convenios_regiao_publicados = convenios_regiao.exclude(data_pub_diario=None)
    convenios_regiao_equipados = convenios_regiao.exclude(data_termo_aceite=None)
    sumario = (
        casas_regiao.count(),
        casas_regiao.exclude(convenio__in=convenios_regiao).distinct().count(),
        casas_regiao.filter(convenio__in=convenios_regiao).distinct().count(),
        casas_regiao.filter(convenio__in=convenios_regiao_publicados).distinct().count(),
        casas_regiao.filter(convenio__in=convenios_regiao_equipados).distinct().count(),
    )

    cabecalho_topo = (
        _(u'UF'),
        _(u'Câmaras municipais'),
        _(u'Não Aderidas'),
        _(u'Aderidas'),
        _(u'Conveniadas'),
        _(u'Equipadas')
    )

    return {
        "linhas": lista,
        "cabecalho": cabecalho_topo,
        "sumario": sumario,
    }

@login_required
def report_regiao(request, regiao='NE'):

    if request.POST:
        if 'regiao' in request.POST:
            regiao = request.POST['regiao']

    REGIAO_CHOICES = dict(UnidadeFederativa.REGIAO_CHOICES)

    projetos = Projeto.objects.all()

    camaras = CasaLegislativa.objects.filter(tipo__sigla='CM')

    tabelas = list()
    # Geral
    convenios = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM')
    tabela = casas_estado_to_tabela(camaras, convenios, regiao)
    tabela["projeto"] = _(u"Geral")

    tabelas.append(tabela)

    for projeto in projetos:
        convenios_proj = convenios.filter(projeto=projeto)
        tabela = casas_estado_to_tabela(camaras, convenios_proj, regiao)
        tabela["projeto"] = projeto.nome
        tabelas.append(tabela)

    data = datetime.datetime.now().strftime('%d/%m/%Y')
    hora = datetime.datetime.now().strftime('%H:%M')
    pisa.showLogging()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=RelatorioRegiao_' + regiao + '.pdf'
    #tabelas = ({'projeto':"PI"},{'projeto':"PML"},)
    t = loader.get_template('convenios/tabela_regiao.html')
    c = Context({'tabelas': tabelas, 'regiao': REGIAO_CHOICES[regiao], 'data': data, 'hora': hora})
    pdf = pisa.CreatePDF(t.render(c), response)
    if not pdf.err:
        pisa.startViewer(response)

    return response

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=convenios.csv'

    csv_writer = csv.writer(response)
    convenios = carrinhoOrGet_for_qs(request)
    if not convenios:
        return HttpResponseRedirect('../')

    atributos = [_(u"No. Processo"), _(u"No. Convênio"), _(u"Projeto"), _(u"Casa Legislativa"), _(u"Data de Adesão"), _(u"Data de Convênio"),
                 _(u"Data da Publicacao no D.O."), _(u"Data Equipada"), ]

    if request.POST:
        atributos = request.POST.getlist("itens_csv_selected")

    col_titles = atributos
    if _(u"Casa Legislativa") in col_titles:
        pos = col_titles.index(_(u"Casa Legislativa")) + 1
        col_titles.insert(pos, _(u"uf"))
    csv_writer.writerow([s.encode("utf-8") for s in col_titles])

    for convenio in convenios:
        lista = []
        for atributo in atributos:
            if _(u"No. Processo") == atributo:
                lista.append(convenio.num_processo_sf.encode("utf-8"))
            elif _(u"No. Convênio") == atributo:
                lista.append(convenio.num_convenio.encode("utf-8"))
            elif _(u"Projeto") == atributo:
                lista.append(convenio.projeto.nome.encode("utf-8"))
            elif _(u"Casa Legislativa") == atributo:
                lista.append(convenio.casa_legislativa.nome.encode("utf-8"))
                lista.append(convenio.casa_legislativa.municipio.uf.sigla.encode("utf-8"))
            elif _(u"Data de Adesão") == atributo:
                data = ''
                if convenio.data_adesao:
                    data = convenio.data_adesao.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
            elif _(u"Data de Convênio") == atributo:
                data = ''
                if convenio.data_retorno_assinatura:
                    data = convenio.data_retorno_assinatura.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
            elif _(u"Data da Publicacao no D.O.") == atributo:
                data = ''
                if convenio.data_pub_diario:
                    data = convenio.data_pub_diario.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
                data = ''
            elif _(u"Data Equipada") == atributo:
                if convenio.data_termo_aceite:
                    data = convenio.data_termo_aceite.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
            else:
                pass

        csv_writer.writerow(lista)

    return response
