# coding: utf-8
import datetime
import csv
import ho.pisa as pisa

from django.template import Context, loader
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.shortcuts import render_to_response, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.parlamentares.reports import ParlamentaresLabels

from geraldo.generators import PDFGenerator


def adicionar_parlamentar_carrinho(request, queryset=None, id=None):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
        if not request.session.has_key('carrinho_parlametar'):
            request.session['carrinho_parlamentar'] = ids_selecionados
        else:
            lista = request.session['carrinho_parlamentar']
            # Verifica se id já não está adicionado
            for id in ids_selecionados:
                if not id in lista:
                    lista.append(id)
            request.session['carrinho_parlamentar'] = lista


@csrf_protect
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

    carrinhoIsEmpty = not(request.session.has_key('carrinho_parlamentares'))

    return render_to_response('parlamentares/carrinho.html',
                              {'MEDIA_URL': settings.MEDIA_URL,
                               'carIsEmpty': carrinhoIsEmpty,
                               'paginas': paginas,
                               'query_str': '?' + request.META['QUERY_STRING']},
                              context_instance=RequestContext(request))


def carrinhoOrGet_for_qs(request):
    """
       Verifica se existe parlamentares na sessão se não verifica get e retorna qs correspondente.
    """
    if request.session.has_key('carrinho_parlamentar'):
        ids = request.session['carrinho_parlamentar']
        qs = Parlamentar.objects.filter(pk__in=ids)
    else:
        qs = Parlamentar.objects.all()
        if request.GET:
            qs = get_for_qs(request.GET, qs)
    return qs


def query_ordena(qs, o, ot):
    list_display = ('nome_completo',)

    aux = list_display[(int(o) - 1)]
    if ot == 'asc':
        qs = qs.order_by(aux)
    else:
        qs = qs.order_by("-" + aux)
    return qs


def get_for_qs(get, qs):
    """
    Verifica atributos do GET e retorna queryset correspondente
    """
    kwargs = {}
    for k, v in get.iteritems():
        if not (k == 'page' or k == 'pop' or k == 'q'):
            if not k == 'o':
                if k == "ot":
                    qs = query_ordena(qs, get["o"], get["ot"])
                else:
                    kwargs[str(k)] = v
                    qs = qs.filter(**kwargs)
    return qs


def deleta_itens_carrinho(request):
    """
    Deleta itens selecionados do carrinho
    """
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
    if request.session.has_key('carrinho_parlamentar'):
        lista = request.session['carrinho_parlamentar']
        for item in ids_selecionados:
            lista.remove(item)
        if lista:
            request.session['carrinho_parlamentar'] = lista
        else:
            del lista
            del request.session['carrinho_parlamentar']

    return HttpResponseRedirect('.')


def labels_report(request, id=None, formato='3x9_etiqueta'):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """

    if request.POST:
        if request.POST.has_key('tipo_etiqueta'):
            tipo = request.POST['tipo_etiqueta']

    if id:
        qs = Parlamentar.objects.filter(pk=id)

    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = ParlamentaresLabels(queryset=qs, formato=formato)
    report.generate_by(PDFGenerator, filename=response)

    return response
