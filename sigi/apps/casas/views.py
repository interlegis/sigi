# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from geraldo.generators import PDFGenerator

from sigi.apps.casas.models import CasaLegislativa, Funcionario
from sigi.apps.casas.reports import CasasLegislativasLabels
from sigi.apps.casas.reports import CasasLegislativasLabelsSemPresidente
from sigi.apps.casas.reports import CasasLegislativasReport
from sigi.apps.casas.reports import CasasSemConvenioReport
from sigi.apps.casas.reports import InfoCasaLegislativa
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.parlamentares.reports import ParlamentaresLabels

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.conf import settings

import csv

# @param qs: queryset
# @param o: (int) number of order field


def query_ordena(qs, o):
    from sigi.apps.casas.admin import CasaLegislativaAdmin
    list_display = CasaLegislativaAdmin.list_display
    order_fields = []

    for order_number in o.split('.'):
        order_number = int(order_number)
        order = ''
        if order_number != abs(order_number):
            order_number = abs(order_number)
            order = '-'
        order_fields.append(order + list_display[order_number - 1])

    qs = qs.order_by(*order_fields)
    return qs


def get_for_qs(get, qs):
    """
        Verifica atributos do GET e retorna queryset correspondente
    """
    kwargs = {}
    for k, v in get.iteritems():
        if str(k) not in ('page', 'pop', 'q', '_popup', 'o', 'ot'):
            kwargs[str(k)] = v

    qs = qs.filter(**kwargs)
    if 'o' in get:
        qs = query_ordena(qs, get['o'])

    return qs


def carrinhoOrGet_for_qs(request):
    """
       Verifica se existe casas na sessão se não verifica get e retorna qs correspondente.
    """
    if request.session.has_key('carrinho_casas'):
        ids = request.session['carrinho_casas']
        qs = CasaLegislativa.objects.filter(pk__in=ids)
    else:
        qs = CasaLegislativa.objects.all()
        if request.GET:
            qs = get_for_qs(request.GET, qs)
    return qs


def adicionar_casas_carrinho(request, queryset=None, id=None):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
        if not request.session.has_key('carrinho_casas'):
            request.session['carrinho_casas'] = ids_selecionados
        else:
            lista = request.session['carrinho_casas']
            # Verifica se id já não está adicionado
            for id in ids_selecionados:
                if not id in lista:
                    lista.append(id)
            request.session['carrinho_casas'] = lista


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

    carrinhoIsEmpty = not(request.session.has_key('carrinho_casas'))

    return render_to_response(
        'casas/carrinho.html',
        {
            'MEDIA_URL': settings.MEDIA_URL,
            'carIsEmpty': carrinhoIsEmpty,
            'paginas': paginas,
            'query_str': '?' + request.META['QUERY_STRING']
        }
    )


def excluir_carrinho(request):
    if request.session.has_key('carrinho_casas'):
        del request.session['carrinho_casas']
    return HttpResponseRedirect('.')


def deleta_itens_carrinho(request):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
        if request.session.has_key('carrinho_casas'):
            lista = request.session['carrinho_casas']
            for item in ids_selecionados:
                lista.remove(item)
            if lista:
                request.session['carrinho_casas'] = lista
            else:
                del lista
                del request.session['carrinho_casas']

    return HttpResponseRedirect('.')


def labels_report(request, id=None, tipo=None, formato='3x9_etiqueta'):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """

    if request.POST:
        if request.POST.has_key('tipo_etiqueta'):
            tipo = request.POST['tipo_etiqueta']
        if request.POST.has_key('tamanho_etiqueta'):
            formato = request.POST['tamanho_etiqueta']

    if tipo == 'sem_presidente':
        return labels_report_sem_presidente(request, id, formato)

    if id:
        qs = CasaLegislativa.objects.filter(pk=id)
    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = CasasLegislativasLabels(queryset=qs, formato=formato)
    report.generate_by(PDFGenerator, filename=response)

    return response


def labels_report_parlamentar(request, id=None, formato='3x9_etiqueta'):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """

    if request.POST:
        if request.POST.has_key('tamanho_etiqueta'):
            formato = request.POST['tamanho_etiqueta']

    if id:
        legislaturas = [c.legislatura_set.latest('data_inicio') for c in CasaLegislativa.objects.filter(pk__in=id, legislatura__id__isnull=False).distinct()]
        mandatos = reduce(lambda x, y: x | y, [l.mandato_set.all() for l in legislaturas])
        parlamentares = [m.parlamentar for m in mandatos]
        qs = parlamentares

    else:
        qs = carrinhoOrGet_for_parlamentar_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = ParlamentaresLabels(queryset=qs, formato=formato)
    report.generate_by(PDFGenerator, filename=response)

    return response


def carrinhoOrGet_for_parlamentar_qs(request):
    """
       Verifica se existe parlamentares na sessão se não verifica get e retorna qs correspondente.
    """
    if request.session.has_key('carrinho_casas'):
        ids = request.session['carrinho_casas']
        legislaturas = [c.legislatura_set.latest('data_inicio') for c in CasaLegislativa.objects.filter(pk__in=ids, legislatura__id__isnull=False).distinct()]
        mandatos = reduce(lambda x, y: x | y, [l.mandato_set.all() for l in legislaturas])
        parlamentares = [m.parlamentar for m in mandatos]
        qs = parlamentares
    else:
        legislaturas = [c.legislatura_set.latest('data_inicio') for c in CasaLegislativa.objects.all().distinct()]
        mandatos = reduce(lambda x, y: x | y, [l.mandato_set.all() for l in legislaturas])
        parlamentares = [m.parlamentar for m in mandatos]
        qs = parlamentares
        if request.GET:
            qs = get_for_qs(request.GET, qs)
    return qs


def labels_report_sem_presidente(request, id=None, formato='2x5_etiqueta'):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """

    if id:
        qs = CasaLegislativa.objects.filter(pk=id)
    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = CasasLegislativasLabelsSemPresidente(queryset=qs, formato=formato)
    report.generate_by(PDFGenerator, filename=response)

    return response


def report(request, id=None, tipo=None):

    if request.POST:
        if request.POST.has_key('tipo_relatorio'):
            tipo = request.POST['tipo_relatorio']

    if tipo == 'completo':
        return report_complete(request, id)

    if id:
        qs = CasaLegislativa.objects.filter(pk=id)
    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    # qs.order_by('municipio__uf','nome')
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = CasasLegislativasReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response


def report_complete(request, id=None):

    if id:
        qs = CasaLegislativa.objects.filter(pk=id)
    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'

    # Gera um relatorio para cada casa e concatena os relatorios
    cont = 0
    canvas = None
    quant = qs.count()
    if quant > 1:
        for i in qs:
            cont += 1
            # queryset deve ser uma lista
            lista = (i,)
            if cont == 1:
                report = InfoCasaLegislativa(queryset=lista)
                canvas = report.generate_by(PDFGenerator, return_canvas=True, filename=response,)
            else:
                report = InfoCasaLegislativa(queryset=lista)
                if cont == quant:
                    report.generate_by(PDFGenerator, canvas=canvas)
                else:
                    canvas = report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
    else:
        report = InfoCasaLegislativa(queryset=qs)
        report.generate_by(PDFGenerator, filename=response)

    return response


def casas_sem_convenio_report(request):
    qs = CasaLegislativa.objects.filter(convenio=None).order_by('municipio__uf', 'nome')

    if request.GET:
        qs = get_for_qs(request.GET, qs)
    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(mimetype='application/pdf')
    report = CasasSemConvenioReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response


def export_csv(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=casas.csv'

    writer = csv.writer(response)

    casas = carrinhoOrGet_for_qs(request)
    if not casas or not request.POST:
        return HttpResponseRedirect('../')

    atributos = request.POST.getlist("itens_csv_selected")
    atributos2 = [s.encode("utf-8") for s in atributos]

    try:
        atributos2.insert(atributos2.index('Município'), u'UF')
    except ValueError:
        pass

    writer.writerow(atributos2)

    for casa in casas:
        lista = []
        contatos = casa.funcionario_set.filter(setor="contato_interlegis")
        for atributo in atributos:
            if u"CNPJ" == atributo:
                lista.append(casa.cnpj.encode("utf-8"))
            elif u"Código IBGE" == atributo:
                lista.append(str(casa.municipio.codigo_ibge).encode("utf-8"))
            elif u"Código TSE" == atributo:
                lista.append(str(casa.municipio.codigo_tse).encode("utf-8"))
            elif u"Nome" == atributo:
                lista.append(casa.nome.encode("utf-8"))
            elif u"Município" == atributo:
                lista.append(unicode(casa.municipio.uf.sigla).encode("utf-8"))
                lista.append(unicode(casa.municipio.nome).encode("utf-8"))
            elif u"Presidente" == atributo:
                # TODO: Esse encode deu erro em 25/04/2012. Comentei para que o usuário pudesse continuar seu trabalho
                # É preciso descobrir o porque do erro e fazer a correção definitiva.
                #                lista.append(str(casa.presidente or "").encode("utf-8"))
                lista.append(str(casa.presidente or ""))
            elif u"Logradouro" == atributo:
                lista.append(casa.logradouro.encode("utf-8"))
            elif u"Bairro" == atributo:
                lista.append(casa.bairro.encode("utf-8"))
            elif u"CEP" == atributo:
                lista.append(casa.cep.encode("utf-8"))
            elif u"Telefone" == atributo:
                lista.append(str(casa.telefone or ""))
            elif u"Página web" == atributo:
                lista.append(casa.pagina_web.encode("utf-8"))
            elif u"Email" == atributo:
                lista.append(casa.email.encode("utf-8"))
            elif u"Número de parlamentares" == atributo:
                lista.append(casa.total_parlamentares)
            elif u"Última alteração de endereco" == atributo:
                lista.append(casa.ult_alt_endereco)
            elif u"Nome contato" == atributo:
                if contatos and contatos[0].nome:
                    lista.append(contatos[0].nome.encode("utf-8"))
                else:
                    lista.append('')
            elif u"Cargo contato" == atributo:
                if contatos and contatos[0].cargo:
                    lista.append(contatos[0].cargo.encode("utf-8"))
                else:
                    lista.append('')
            elif u"Email contato" == atributo:
                if contatos and contatos[0].email:
                    lista.append(contatos[0].email.encode("utf-8"))
                else:
                    lista.append('')
            else:
                pass

        writer.writerow(lista)

    return response
