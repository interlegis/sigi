# -*- coding: utf-8 -*-
import csv
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from geraldo.generators import PDFGenerator

from sigi.apps.casas.forms import PortfolioForm
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.casas.reports import (CasasLegislativasLabels,
                                     CasasLegislativasLabelsSemPresidente,
                                     CasasLegislativasReport,
                                     CasasSemConvenioReport,
                                     InfoCasaLegislativa)
from sigi.apps.contatos.models import (Mesorregiao, Microrregiao,
                                       UnidadeFederativa)
from sigi.apps.ocorrencias.models import Ocorrencia
from sigi.apps.parlamentares.reports import ParlamentaresLabels
from sigi.apps.servicos.models import TipoServico
from sigi.apps.servidores.models import Servidor


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
    if 'carrinho_casas' in request.session:
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
        if 'carrinho_casas' not in request.session:
            request.session['carrinho_casas'] = ids_selecionados
        else:
            lista = request.session['carrinho_casas']
            # Verifica se id já não está adicionado
            for id in ids_selecionados:
                if id not in lista:
                    lista.append(id)
            request.session['carrinho_casas'] = lista

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

    carrinhoIsEmpty = not('carrinho_casas' in request.session)

    return render(
        request,
        'casas/carrinho.html',
        {
            'carIsEmpty': carrinhoIsEmpty,
            'paginas': paginas,
            'query_str': '?' + request.META['QUERY_STRING']
        }
    )

@login_required
def excluir_carrinho(request):
    if 'carrinho_casas' in request.session:
        del request.session['carrinho_casas']
    return HttpResponseRedirect('.')

@login_required
def deleta_itens_carrinho(request):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')
        if 'carrinho_casas' in request.session:
            lista = request.session['carrinho_casas']
            for item in ids_selecionados:
                lista.remove(item)
            if lista:
                request.session['carrinho_casas'] = lista
            else:
                del lista
                del request.session['carrinho_casas']

    return HttpResponseRedirect('.')

@login_required
def labels_report(request, id=None, tipo=None, formato='3x9_etiqueta'):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """

    if request.POST:
        if 'tipo_etiqueta' in request.POST:
            tipo = request.POST['tipo_etiqueta']
        if 'tamanho_etiqueta' in request.POST:
            formato = request.POST['tamanho_etiqueta']

    if tipo == 'sem_presidente':
        return labels_report_sem_presidente(request, id, formato)

    if id:
        qs = CasaLegislativa.objects.filter(pk=id)
    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = CasasLegislativasLabels(queryset=qs, formato=formato)
    report.generate_by(PDFGenerator, filename=response)

    return response

@login_required
def labels_report_parlamentar(request, id=None, formato='3x9_etiqueta'):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """

    if request.POST:
        if 'tamanho_etiqueta' in request.POST:
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

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = ParlamentaresLabels(queryset=qs, formato=formato)
    report.generate_by(PDFGenerator, filename=response)

    return response


def carrinhoOrGet_for_parlamentar_qs(request):
    """
       Verifica se existe parlamentares na sessão se não verifica get e retorna qs correspondente.
    """
    if 'carrinho_casas' in request.session:
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

@login_required
def labels_report_sem_presidente(request, id=None, formato='2x5_etiqueta'):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """

    if id:
        qs = CasaLegislativa.objects.filter(pk=id)
    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = CasasLegislativasLabelsSemPresidente(queryset=qs, formato=formato)
    report.generate_by(PDFGenerator, filename=response)

    return response

@login_required
def report(request, id=None, tipo=None):

    if request.POST:
        if 'tipo_relatorio' in request.POST:
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
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=casas.pdf'
    report = CasasLegislativasReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response

@login_required
def report_complete(request, id=None):

    if id:
        qs = CasaLegislativa.objects.filter(pk=id)
    else:
        qs = carrinhoOrGet_for_qs(request)

    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(content_type='application/pdf')
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

@login_required
def casas_sem_convenio_report(request):
    qs = CasaLegislativa.objects.filter(convenio=None).order_by('municipio__uf', 'nome')

    if request.GET:
        qs = get_for_qs(request.GET, qs)
    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(content_type='application/pdf')
    report = CasasSemConvenioReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=casas.csv'

    writer = csv.writer(response)

    casas = carrinhoOrGet_for_qs(request)
    if not casas or not request.POST:
        return HttpResponseRedirect('../')

    atributos = request.POST.getlist("itens_csv_selected")
    atributos2 = [s.encode("utf-8") for s in atributos]

    try:
        atributos2.insert(atributos2.index(_(u'Município')), _(u'UF'))
    except ValueError:
        pass

    writer.writerow(atributos2)

    for casa in casas:
        lista = []
        contatos = casa.funcionario_set.filter(setor="contato_interlegis")
        for atributo in atributos:
            if _(u"CNPJ") == atributo:
                lista.append(casa.cnpj.encode("utf-8"))
            elif _(u"Código IBGE") == atributo:
                lista.append(str(casa.municipio.codigo_ibge).encode("utf-8"))
            elif _(u"Código TSE") == atributo:
                lista.append(str(casa.municipio.codigo_tse).encode("utf-8"))
            elif _(u"Nome") == atributo:
                lista.append(casa.nome.encode("utf-8"))
            elif _(u"Município") == atributo:
                lista.append(unicode(casa.municipio.uf.sigla).encode("utf-8"))
                lista.append(unicode(casa.municipio.nome).encode("utf-8"))
            elif _(u"Presidente") == atributo:
                # TODO: Esse encode deu erro em 25/04/2012. Comentei para que o usuário pudesse continuar seu trabalho
                # É preciso descobrir o porque do erro e fazer a correção definitiva.
                #                lista.append(str(casa.presidente or "").encode("utf-8"))
                lista.append(str(casa.presidente or ""))
            elif _(u"Logradouro") == atributo:
                lista.append(casa.logradouro.encode("utf-8"))
            elif _(u"Bairro") == atributo:
                lista.append(casa.bairro.encode("utf-8"))
            elif _(u"CEP") == atributo:
                lista.append(casa.cep.encode("utf-8"))
            elif _(u"Telefone") == atributo:
                lista.append(str(casa.telefone or ""))
            elif _(u"Página web") == atributo:
                lista.append(casa.pagina_web.encode("utf-8"))
            elif _(u"Email") == atributo:
                lista.append(casa.email.encode("utf-8"))
            elif _(u"Número de parlamentares") == atributo:
                lista.append(casa.total_parlamentares)
            elif _(u"Última alteração de endereco") == atributo:
                lista.append(casa.ult_alt_endereco)
            elif _(u"Nome contato") == atributo:
                if contatos and contatos[0].nome:
                    lista.append(contatos[0].nome.encode("utf-8"))
                else:
                    lista.append('')
            elif _(u"Cargo contato") == atributo:
                if contatos and contatos[0].cargo:
                    lista.append(contatos[0].cargo.encode("utf-8"))
                else:
                    lista.append('')
            elif _(u"Email contato") == atributo:
                if contatos and contatos[0].email:
                    lista.append(contatos[0].email.encode("utf-8"))
                else:
                    lista.append('')
            else:
                pass

        writer.writerow(lista)

    return response

@login_required
def portfolio(request):
    page = request.GET.get('page', 1)
    regiao = request.GET.get('regiao', None)
    uf_id = request.GET.get('uf', None)
    meso_id = request.GET.get('meso', None)
    micro_id = request.GET.get('micro', None)
    
    data = {}
    data['errors'] = []
    data['messages'] = []
    data['regioes'] = UnidadeFederativa.REGIAO_CHOICES
    casas = None
    gerente_contas = None
    
    if request.method == 'POST':
        form = PortfolioForm(data=request.POST)
        if form.is_valid():
            gerente_contas = form.cleaned_data['gerente_contas']
        else:
            data['errors'].append(_(u"Dados inválidos"))
        
    if micro_id:
        microrregiao = get_object_or_404(Microrregiao, pk=micro_id)
        mesorregiao = microrregiao.mesorregiao 
        uf = mesorregiao.uf
        data['regiao'] = uf.regiao
        data['uf_id'] = uf.pk
        data['meso_id'] = mesorregiao.pk
        data['micro_id'] = microrregiao.pk
        data['ufs'] = UnidadeFederativa.objects.filter(regiao=uf.regiao)
        data['mesorregioes'] = uf.mesorregiao_set.all()
        data['microrregioes'] = mesorregiao.microrregiao_set.all()
        data['form'] = PortfolioForm(_(u'Atribuir casas da microrregiao %s para') % (unicode(microrregiao),))
        data['querystring'] = 'micro=%s' %  (microrregiao.pk,)
        casas = CasaLegislativa.objects.filter(municipio__microrregiao=microrregiao)
    elif meso_id:
        mesorregiao = get_object_or_404(Mesorregiao, pk=meso_id)
        uf = mesorregiao.uf
        data['regiao'] = uf.regiao
        data['uf_id'] = uf.pk
        data['meso_id'] = mesorregiao.pk
        data['ufs'] = UnidadeFederativa.objects.filter(regiao=uf.regiao)
        data['mesorregioes'] = uf.mesorregiao_set.all()
        data['microrregioes'] = mesorregiao.microrregiao_set.all()
        data['form'] = PortfolioForm(_(u'Atribuir casas da mesorregiao %s para') % (unicode(mesorregiao),))
        data['querystring'] = 'meso=%s' %  (mesorregiao.pk,)
        casas = CasaLegislativa.objects.filter(municipio__microrregiao__mesorregiao=mesorregiao)
    elif uf_id:
        uf = get_object_or_404(UnidadeFederativa, pk=uf_id)
        data['regiao'] = uf.regiao
        data['uf_id'] = uf.pk
        data['ufs'] = UnidadeFederativa.objects.filter(regiao=uf.regiao)
        data['mesorregioes'] = uf.mesorregiao_set.all()
        data['form'] = PortfolioForm(_(u'Atribuir casas do estado %s para') % (unicode(uf),))
        data['querystring'] = 'uf=%s' %  (uf.pk,)
        casas = CasaLegislativa.objects.filter(municipio__uf=uf)
    elif regiao:
        data['regiao'] = regiao 
        data['ufs'] = UnidadeFederativa.objects.filter(regiao=regiao)
        data['form'] = PortfolioForm(_(u'Atribuir casas da região %s para') % [x[1] for x in UnidadeFederativa.REGIAO_CHOICES if x[0]==regiao][0])
        data['querystring'] = 'regiao=%s' %  (regiao,)
        casas = CasaLegislativa.objects.filter(municipio__uf__regiao=regiao)
        
    if casas:
        if gerente_contas:
            count = casas.update(gerente_contas=gerente_contas)
            data['messages'].append(ungettext(
                u"%(count)s casa atribuída para %(name)s",
                u"%(count)s casas atribuídas para %(name)s",
                count) % {'count': count, 'name': unicode(gerente_contas)})
        
        casas = casas.order_by('municipio__uf', 'municipio__microrregiao__mesorregiao',
                               'municipio__microrregiao', 'municipio')
        
        casas.prefetch_related('municipio', 'municipio__uf', 'municipio__microrregiao',
                               'municipio__microrregiao__mesorregiao', 'gerente_contas')
        
        paginator = Paginator(casas, 30)
        try:
            pagina = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pagina = paginator.page(paginator.num_pages)
        data['page_obj'] = pagina
        
    return render(request, 'casas/portfolio.html', data)


def resumo_carteira(casas):
    regioes = {r[0]: 0 for r in UnidadeFederativa.REGIAO_CHOICES}
    regioes['total'] = 0
    total = regioes.copy()
    sem_produto = regioes.copy()
    tipos_servico = TipoServico.objects.all()
    dados = {ts.id: regioes.copy() for ts in tipos_servico}
    
    for r in casas.values('municipio__uf__regiao').annotate(quantidade=Count('id')).order_by():
        regiao = r['municipio__uf__regiao']
        quantidade = r['quantidade']
        total[regiao] = quantidade
        total['total'] += quantidade
    
    for r in casas.values('municipio__uf__regiao', 'servico__tipo_servico__id').annotate(quantidade=Count('id')).order_by():
        regiao = r['municipio__uf__regiao']
        servico = r['servico__tipo_servico__id']
        quantidade = r['quantidade']
        if servico is None:
            sem_produto[regiao] = quantidade
            sem_produto['total'] += quantidade
        else:
            dados[servico][regiao] = quantidade 
            dados[servico]['total'] += quantidade
    
    dados_ocorrencia = {
        'registradas': regioes.copy(),
        'pendentes': regioes.copy(),
        'sem': regioes.copy(),
        'media': regioes.copy(),
    }
    
    for r in casas.values('ocorrencia__status', 'municipio__uf__regiao').annotate(quantidade=Count('id')).order_by():
        status = r['ocorrencia__status']
        regiao = r['municipio__uf__regiao']
        quantidade = r['quantidade']
        if status is None:
            dados_ocorrencia['sem'][regiao] += quantidade
            dados_ocorrencia['sem']['total'] += quantidade
        else:
            dados_ocorrencia['registradas'][regiao] += quantidade
            dados_ocorrencia['registradas']['total'] += quantidade
            if status in [Ocorrencia.STATUS_ABERTO, Ocorrencia.STATUS_REABERTO]:
                dados_ocorrencia['pendentes'][regiao] += quantidade
                dados_ocorrencia['pendentes']['total'] += quantidade
            
    for r in regioes:
        if (total[r] - dados_ocorrencia['sem'][r]) == 0:
            dados_ocorrencia['media'][r] = 0
        else:
            dados_ocorrencia['media'][r] = (1.0 * dados_ocorrencia['registradas'][r] / (total[r] - dados_ocorrencia['sem'][r]))
         
    resumo = [[_(u"Item"), _(u"Total nacional")] + [r[1] for r in UnidadeFederativa.REGIAO_CHOICES]]
    resumo.append([_(u"Casas em sua carteira"), total['total']] + [total[r[0]] for r in UnidadeFederativa.REGIAO_CHOICES])
    resumo.append({'subtitle': _(u"Uso dos produtos Interlegis")})
    resumo.append([_(u"Casas sem nenhum produto"), sem_produto['total']] + [sem_produto[r[0]] for r in UnidadeFederativa.REGIAO_CHOICES])
    resumo.extend([[ts.nome, dados[ts.id]['total']]+[dados[ts.id][r[0]] for r in UnidadeFederativa.REGIAO_CHOICES] for ts in tipos_servico])
    resumo.append({'subtitle': _(u"Registros no sistema de ocorrências")})
    resumo.append([_(u"Casas que nunca registraram ocorrências"), dados_ocorrencia['sem']['total']]+[dados_ocorrencia['sem'][r[0]] for r in UnidadeFederativa.REGIAO_CHOICES])
    resumo.append([_(u"Total de ocorrências registradas"), dados_ocorrencia['registradas']['total']]+[dados_ocorrencia['registradas'][r[0]] for r in UnidadeFederativa.REGIAO_CHOICES])
    resumo.append([_(u"Total de ocorrências pendentes"), dados_ocorrencia['pendentes']['total']]+[dados_ocorrencia['pendentes'][r[0]] for r in UnidadeFederativa.REGIAO_CHOICES])
    resumo.append([_(u"Média de ocorrências por casa"), round(dados_ocorrencia['media']['total'],2)]+[round(dados_ocorrencia['media'][r[0]],2) for r in UnidadeFederativa.REGIAO_CHOICES])

    return resumo


def casas_carteira(request, casas, context):
    servicos = request.GET.getlist('servico')
    sigla_regiao = request.GET.get('r', None)
    sigla_uf = request.GET.get('uf', None)
    meso_id = request.GET.get('meso', None)
    micro_id = request.GET.get('micro', None)
    servicos = request.GET.getlist('servico')
    tipos_servico = context['servicos']
    
    context['qs_regiao'] = ''

    if micro_id is not None:
        context['micro'] = get_object_or_404(Microrregiao, pk=micro_id)
        context['qs_regiao'] = 'micro=%s' % micro_id
        context['meso'] = context['micro'].mesorregiao
        context['uf'] = context['meso'].uf
        context['regiao'] = context['uf'].regiao
        casas = casas.filter(municipio__microrregiao=context['micro'])
    elif meso_id is not None:
        context['meso'] = get_object_or_404(Mesorregiao, pk=meso_id)
        context['qs_regiao'] = 'meso=%s' % meso_id
        context['uf'] = context['meso'].uf
        context['regiao'] = context['uf'].regiao
        casas = casas.filter(municipio__microrregiao__mesorregiao=context['meso'])
    elif sigla_uf is not None:
        context['uf'] = get_object_or_404(UnidadeFederativa, sigla=sigla_uf)
        context['qs_regiao'] = 'uf=%s' % sigla_uf
        context['regiao'] = context['uf'].regiao
        casas = casas.filter(municipio__uf=context['uf'])
    elif sigla_regiao is not None:
        context['regiao'] = sigla_regiao
        context['qs_regiao'] = 'r=%s' % sigla_regiao
        casas = casas.filter(municipio__uf__regiao=sigla_regiao)
         
    if 'regiao' in context:
        context['ufs'] = UnidadeFederativa.objects.filter(regiao=context['regiao'])
         
    todos_servicos = ['_none_'] + [s.sigla for s in tipos_servico]
    
    if not servicos or set(servicos) == set(todos_servicos):
        servicos = todos_servicos
        context['qs_servico'] = ''
    else:
        if '_none_' in servicos:
            casas = casas.filter(Q(servico=None) | Q(servico__tipo_servico__sigla__in=servicos))
        else:
            casas = casas.filter(servico__tipo_servico__sigla__in=servicos)
        casas = casas.distinct('nome', 'municipio__uf')
        context['qs_servico'] = "&".join(['servico=%s' %s for s in servicos])
 
    context['servicos_check'] = servicos
     
    casas = casas.select_related('municipio', 'municipio__uf', 'municipio__microrregiao', 'municipio__microrregiao__mesorregiao').prefetch_related('servico_set')

    return casas, context

@login_required
def painel_relacionamento(request):
    page = request.GET.get('page', 1)
    snippet = request.GET.get('snippet', '')
    seletor = request.GET.get('s', None)
    servidor = request.GET.get('servidor', None)
    format = request.GET.get('f', 'html')
    
    if servidor is None:
        gerente = request.user.servidor
    elif servidor == '_all':
        gerente = None
    else:
        gerente = get_object_or_404(Servidor, pk=servidor)

    if gerente is not None:
        casas = gerente.casas_que_gerencia.all()

    if gerente is None or not casas.exists():
        casas = CasaLegislativa.objects.exclude(gerente_contas=None)
        gerente = None
        
    tipos_servico = TipoServico.objects.all()
    regioes = UnidadeFederativa.REGIAO_CHOICES

    context = {
        'seletor': seletor,
        'snippet': snippet,
        'regioes': regioes,
        'servicos': tipos_servico,
        'gerentes': Servidor.objects.exclude(casas_que_gerencia=None),
        'gerente': gerente,
        'qs_servidor': ('servidor=%s' % gerente.pk) if gerente else '', 
    }
    
    if snippet != 'lista':
        context['resumo'] = resumo_carteira(casas)

    if snippet != 'resumo':    
        casas, context = casas_carteira(request, casas, context)
        paginator = Paginator(casas, 30)
        try:
            pagina = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pagina = paginator.page(paginator.num_pages)
        context['page_obj'] = pagina

    if snippet == 'lista':
        if format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=casas.csv'
            writer = csv.writer(response)
            writer.writerow([
                _(u"Casa legislativa").encode('utf8'),
                _(u"Região").encode('utf8'),
                _(u"Estado").encode('utf8'),
                _(u"Mesorregião").encode('utf8'),
                _(u"Microrregião").encode('utf8'),
                _(u"Gerente de relacionamento").encode('utf8'),
                _(u"Serviços").encode('utf8'),
            ])
            for c in casas:
                writer.writerow([
                    c.nome.encode('utf8'),
                    c.municipio.uf.get_regiao_display().encode('utf8'),
                    c.municipio.uf.sigla.encode('utf8'),
                    c.municipio.microrregiao.mesorregiao.nome.encode('utf8'),
                    c.municipio.microrregiao.nome.encode('utf8'),
                    c.gerente_contas.nome_completo.encode('utf8'),
                    (u", ".join([s.tipo_servico.nome for s in c.servico_set.filter(data_desativacao__isnull=True)])).encode('utf8'),
                ])
            return response
        return render(request, 'casas/lista_casas_carteira_snippet.html', context)
    if snippet == 'resumo':
        return render(request, 'casas/resumo_carteira_snippet.html', context)
    
    return render(request, 'casas/painel.html', context)
