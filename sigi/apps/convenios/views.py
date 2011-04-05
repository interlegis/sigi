#-*- coding:utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_list_or_404
from geraldo.generators import PDFGenerator
from sigi.apps.convenios.models import Convenio
from sigi.apps.convenios.reports import ConvenioReport      \
                                        ,ConvenioPorCMReport      \
                                        ,ConvenioPorALReport      \
                                        ,ConvenioReportSemAceiteAL \
                                        ,ConvenioReportSemAceiteCM 
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import UnidadeFederativa

import ho.pisa as pisa
from django.template import Context, loader

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.conf import settings

import datetime

def query_ordena(qs,o,ot):
    list_display = ('num_convenio', 'casa_legislativa',
                    'data_adesao','data_retorno_assinatura','data_termo_aceite',
                    'projeto',
                    )

    aux = list_display[(int(o)-1)]
    if ot =='asc':
        qs = qs.order_by(aux)
    else:
        qs = qs.order_by("-"+aux)
    return qs

def get_for_qs(get,qs):
    kwargs = {}
    ids = 0
    for k,v in get.iteritems():
        if not (k == 'page' or k == 'pop' or k == 'q'):
            if not k == 'o':
                if k == "ot":
                    qs = query_ordena(qs,get["o"],get["ot"])
                else:
                    kwargs[str(k)] = v
                    if(str(k)=='ids'):
                        ids = 1
                        break
                    qs = qs.filter(**kwargs)

    if ids:
        query = 'id IN ('+ kwargs['ids'].__str__()+')'
        qs = Convenio.objects.extra(where=[query])
    return qs

def carrinhoOrGet_for_qs(request):
    """
       Verifica se existe convênios na sessão se não verifica get e retorna qs correspondente.
    """    
    if request.session.has_key('carrinho_convenios'):
        ids = request.session['carrinho_convenios']                
        qs = Convenio.objects.filter(pk__in=ids)    
    else:
        qs = Convenio.objects.all()        
        if request.GET:
            qs = qs.order_by("casa_legislativa__municipio__uf","casa_legislativa__municipio")
            qs = get_for_qs(request.GET,qs)
    return qs

def adicionar_convenios_carrinho(request,queryset=None,id=None):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')            
        if not request.session.has_key('carrinho_convenios'):
            request.session['carrinho_convenios'] = ids_selecionados
        else:
            lista = request.session['carrinho_convenios']
            # Verifica se id já não está adicionado
            for id in ids_selecionados:
                if not id in lista:
                    lista.append(id)                                        
            request.session['carrinho_convenios'] = lista       
            
def excluir_carrinho(request):
    if request.session.has_key('carrinho_convenios'):
        del request.session['carrinho_convenios']
    return HttpResponseRedirect('.')

def deleta_itens_carrinho(request):
    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('_selected_action')            
        if request.session.has_key('carrinho_convenios'):            
            lista = request.session['carrinho_convenios']                                        
            for item in ids_selecionados:
                lista.remove(item)
            if lista:                
                request.session['carrinho_convenios'] = lista
            else:
                del lista;
                del request.session['carrinho_convenios']                    
    
    return HttpResponseRedirect('.')

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
        
    carrinhoIsEmpty = not(request.session.has_key('carrinho_convenios'))
        
    return render_to_response(
        'convenios/carrinho.html',
        {
             "ADMIN_MEDIA_PREFIX":settings.ADMIN_MEDIA_PREFIX,
             'MEDIA_URL':settings.MEDIA_URL,
             'carIsEmpty':carrinhoIsEmpty,
             'paginas':paginas,
             'query_str':'?'+request.META['QUERY_STRING']
        }
    )
    
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
        if request.POST.has_key('filtro_casa'):
            tipo = request.POST['filtro_casa']
        if request.POST.has_key('data_aceite'):
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
            
         
    response = HttpResponse(mimetype='application/pdf')
    if report:    
        report.generate_by(PDFGenerator, filename=response)
    else:
        return HttpResponseRedirect('../') 
    return response    

def report_regiao(request,regiao='NE'):
    
    if request.POST:
        if request.POST.has_key('regiao'):
            regiao = request.POST['regiao']

    REGIAO_CHOICES = {
        'SL': 'Sul',
        'SD': 'Sudeste',
        'CO': 'Centro-Oeste',
        'NE': 'Nordeste',
        'NO': 'Norte',
    }   
    
    camaras = CasaLegislativa.objects.filter(tipo__sigla='CM')
    convenios = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM',projeto__sigla='PI')
    
    camaras_sem_processo = camaras.exclude(convenio__projeto__sigla='PI')    
    
    convenios_assinados = convenios.exclude(data_retorno_assinatura=None)
    convenios_em_andamento = convenios.filter(data_retorno_assinatura=None)

    convenios_sem_adesao = convenios.filter(data_adesao=None)
    convenios_com_adesao = convenios.exclude(data_adesao=None)

    convenios_com_aceite = convenios.exclude(data_termo_aceite=None)
    
    # Contando casas por estado
    estados = get_list_or_404(UnidadeFederativa,regiao=regiao)
    
    class LinhaEstado():
        pass
    
    lista = []
    
    for estado in estados:
        linha = LinhaEstado()        
        conv_sem_adesao_est = convenios_sem_adesao.filter(casa_legislativa__municipio__uf=estado)
        conv_com_adesao_est = convenios_com_adesao.filter(casa_legislativa__municipio__uf=estado)
        conv_assinados_est  = convenios_assinados.filter(casa_legislativa__municipio__uf=estado)
        conv_em_andamento_est = convenios_em_andamento.filter(casa_legislativa__municipio__uf=estado)
        conv_equipadas_est = convenios_com_aceite.filter(casa_legislativa__municipio__uf=estado)
                
        camaras_est = camaras.filter(municipio__uf=estado,tipo__sigla='CM').count()
        camaras_sem_processo_est = camaras_sem_processo.filter(municipio__uf=estado).count()    
        camaras_nao_aderidas_est = camaras.filter(convenio__in=conv_sem_adesao_est).count()
        camaras_aderidas_est = camaras.filter(convenio__in=conv_com_adesao_est).count()
        camaras_convenios_assinados_est = camaras.filter(convenio__in=conv_assinados_est).count()
        camaras_convenios_em_andamento_est = camaras.filter(convenio__in=conv_em_andamento_est).count()
        camaras_equipadas_est = camaras.filter(convenio__in=conv_equipadas_est).count()
        
        linha.lista = (
            camaras_est,
            camaras_sem_processo_est,
            camaras_nao_aderidas_est,
            camaras_aderidas_est,
            camaras_convenios_assinados_est,
            camaras_convenios_em_andamento_est,
            camaras_equipadas_est,
        )
        
        linha.estado = estado.sigla
        
        lista.append(linha)
    # Total
    total_cm = camaras.filter(municipio__uf__regiao=regiao,tipo__sigla='CM').count()
    total_sem_processo = camaras_sem_processo.filter(municipio__uf__regiao=regiao).count()
    total_sem_adesao = camaras.filter(convenio__in=convenios_sem_adesao,municipio__uf__regiao=regiao).count()
    total_com_adesao = camaras.filter(convenio__in=convenios_com_adesao,municipio__uf__regiao=regiao).count()
    total_conv_assin = camaras.filter(convenio__in=convenios_assinados,municipio__uf__regiao=regiao).count()
    total_conv_andam = camaras.filter(convenio__in=convenios_em_andamento,municipio__uf__regiao=regiao).count()
    total_equipadas  = camaras.filter(convenio__in=convenios_com_aceite,municipio__uf__regiao=regiao).count()
    
    sumario = [
           total_cm,
           total_sem_processo,
           total_sem_adesao,
           total_com_adesao,
           total_conv_assin,
           total_conv_andam,
           total_equipadas,
    ]
    
        
        
    
    cabecalho_topo = (
        u'UF',              
        u'Câmaras municipais',
        u'Sem processo',
        u'Sem adesão',
        u'Com adesão',
        u'Convênios assinados',
        u'Convênios andamento',
        u'Equipadas'
    )    
    
    projeto = "Projeto Interlegis"
    
    tabela = {
        "regiao":REGIAO_CHOICES[regiao],
        "linhas":lista,
        "cabecalho":cabecalho_topo,
        "sumario":sumario,
        "projeto":projeto,
    }    
    
    data = datetime.datetime.now().strftime('%d/%m/%Y')
    hora = datetime.datetime.now().strftime('%H:%M')    
    pisa.showLogging()
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=RelatorioRegiao_' + regiao + '.pdf'
    t = loader.get_template('convenios/tabela_regiao.html')
    c = Context({'tabela':tabela,'data':data,'hora':hora})
    pdf = pisa.CreatePDF(t.render(c),response)
    if not pdf.err:
        pisa.startViewer(response)

    return response
     
