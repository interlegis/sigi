#-*- coding:utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_list_or_404
from geraldo.generators import PDFGenerator
from sigi.apps.convenios.models import Convenio, Projeto
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

import csv

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

def casas_estado_to_tabela(casas,convenios,regiao):


    estados = get_list_or_404(UnidadeFederativa,regiao=regiao)

    class LinhaEstado():
        pass

    lista = []

    for estado in estados:
        linha = LinhaEstado()

        convenios_est = convenios.filter(casa_legislativa__municipio__uf=estado)
        convenios_est_publicados = convenios_est.exclude(data_pub_diario=None)

        casas_est = casas.filter(municipio__uf=estado)
        casas_est_nao_aderidas = casas_est.exclude(convenio__in=convenios_est).distinct()
        casas_est_aderidas = casas_est.filter(convenio__in=convenios_est).distinct()
        casas_est_conveniadas = casas_est.filter(convenio__in=convenios_est_publicados).distinct()

        linha.lista = (
            casas_est.count(),
            casas_est_nao_aderidas.count(),
            casas_est_aderidas.count(),
            casas_est_conveniadas.count(),
        )

        linha.estado = estado

        lista.append(linha)
        
    casas_regiao = casas.filter(municipio__uf__regiao=regiao)
    convenios_regiao = convenios.filter(casa_legislativa__municipio__uf__regiao=regiao)
    convenios_regiao_publicados = convenios_regiao.exclude(data_pub_diario=None)
    sumario = (
        casas_regiao.count(),
        casas_regiao.exclude(convenio__in=convenios_regiao).distinct().count(),
        casas_regiao.filter(convenio__in=convenios_regiao).distinct().count(),
        casas_regiao.filter(convenio__in=convenios_regiao_publicados).distinct().count(),
    )

    cabecalho_topo = (
        u'UF',
        u'Câmaras municipais',
        u'Não Aderidas',
        u'Aderidas',        
        u'Conveniadas',
    )   

    return {
        "linhas":lista,
        "cabecalho":cabecalho_topo,
        "sumario":sumario,
    }

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
    
    projetos = Projeto.objects.all()
    
    camaras = CasaLegislativa.objects.filter(tipo__sigla='CM')

    tabelas = list()
    # Geral
    convenios = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM')    
    tabela = casas_estado_to_tabela(camaras,convenios,regiao)
    tabela["projeto"] = "Geral"

    tabelas.append(tabela)

    for projeto in projetos:
        convenios_proj = convenios.filter(projeto=projeto)
        tabela = casas_estado_to_tabela(camaras, convenios_proj,regiao)
        tabela["projeto"] = projeto.nome
        tabelas.append(tabela)
    
    data = datetime.datetime.now().strftime('%d/%m/%Y')
    hora = datetime.datetime.now().strftime('%H:%M')    
    pisa.showLogging()
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=RelatorioRegiao_' + regiao + '.pdf'
    #tabelas = ({'projeto':"PI"},{'projeto':"PML"},)
    t = loader.get_template('convenios/tabela_regiao.html')
    c = Context({'tabelas':tabelas,'regiao':REGIAO_CHOICES[regiao],'data':data,'hora':hora})    
    pdf = pisa.CreatePDF(t.render(c),response)
    if not pdf.err:
        pisa.startViewer(response)

    return response

def export_csv(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=convenios.csv'

    csv_writer = csv.writer(response)
    convenios = carrinhoOrGet_for_qs(request)
    if not convenios:
        return HttpResponseRedirect('../')

    if request.POST:
        atributos = request.POST.getlist("itens_csv_selected")
	atributos2 = [s.encode("utf-8") for s in atributos]
        csv_writer.writerow(atributos2)

    for convenio in convenios:
        lista = []
        for atributo in atributos:
            if u"No. Processo" == atributo:
                lista.append(convenio.num_processo_sf.encode("utf-8"))
            elif u"No. Convênio" == atributo:
                lista.append(convenio.num_convenio.encode("utf-8"))
            elif u"Projeto" == atributo:
                lista.append(convenio.projeto.nome.encode("utf-8"))
            elif u"Casa Legislativa" == atributo:
                lista.append(convenio.casa_legislativa.nome.encode("utf-8"))
            elif u"Data de Adesão" == atributo:
                data = ''
                if convenio.data_adesao:
                    data = convenio.data_adesao.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
            elif u"Data de Convênio" == atributo:
                data = ''
                if convenio.data_retorno_assinatura:
                    data = convenio.data_retorno_assinatura.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
            elif u"Data da Publicacao no D.O." == atributo:
                data = ''
                if convenio.data_pub_diario:
                    data = convenio.data_pub_diario.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
                data = ''
            elif u"Data Equipada" == atributo:
                if convenio.data_termo_aceite:
                    data = convenio.data_termo_aceite.strftime("%d/%m/%Y")
                lista.append(data.encode("utf-8"))
            else:
                pass

        csv_writer.writerow(lista)

    return response
     
