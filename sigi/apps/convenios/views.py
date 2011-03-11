from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_list_or_404
from geraldo.generators import PDFGenerator
from sigi.apps.convenios.models import Convenio
from sigi.apps.convenios.reports import ConvenioReport,      \
                                        ConvenioPorCMReport, \
                                        ConvenioPorALReport,  \
                                        ConvenioReportRegiao,     \
                                        ConvenioReportSemAceiteAL, \
                                        ConvenioReportSemAceiteCM 
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import UnidadeFederativa

import ho.pisa as pisa
from django.template import Context, loader

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

def report_por_cm(request, id=None):
    qs = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM').order_by('casa_legislativa__municipio__uf','casa_legislativa')
    if id:
        qs = qs.filter(pk=id)
    elif request.GET: #Se tiver algum parametro de pesquisa
        qs = get_for_qs(request.GET,qs)
    if not qs:
        return HttpResponseRedirect('../')    
    response = HttpResponse(mimetype='application/pdf')
    report = ConvenioPorCMReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response

def report_por_al(request, id=None):
    qs = Convenio.objects.filter(casa_legislativa__tipo__sigla='AL').order_by('casa_legislativa__municipio__uf','casa_legislativa')
    if id:
        qs = qs.filter(pk=id)
    elif request.GET: #Se tiver algum parametro de pesquisa
        qs = get_for_qs(request.GET,qs)
    if not qs:
        return HttpResponseRedirect('../')
    response = HttpResponse(mimetype='application/pdf')
    report = ConvenioPorALReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response

def report_semaceite_por_cm(request, id=None):
    qs = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM').order_by('casa_legislativa__municipio__uf','casa_legislativa')
    if id:
        qs = qs.filter(pk=id)
    elif request.GET: #Se tiver algum parametro de pesquisa
        qs = get_for_qs(request.GET,qs)
    if not qs:
        return HttpResponseRedirect('../')    
    response = HttpResponse(mimetype='application/pdf')
    report = ConvenioReportSemAceiteCM(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response

def report_semaceite_por_al(request, id=None):
    qs = Convenio.objects.filter(casa_legislativa__tipo__sigla='AL').order_by('casa_legislativa__municipio__uf','casa_legislativa')
    if id:
        qs = qs.filter(pk=id)
    elif request.GET: #Se tiver algum parametro de pesquisa
        qs = get_for_qs(request.GET,qs)
    if not qs:
        return HttpResponseRedirect('../')    
    response = HttpResponse(mimetype='application/pdf')
    report = ConvenioReportSemAceiteAL(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response
    

class RelatorioRegiao(object):
    def __init__(self, estado, casas, casas_aderidas, casas_equipadas,casas_nao_equipadas):
        self.estado = estado
        self.quant_casas = casas
        self.quant_casas_aderidas = casas_aderidas
        self.quant_casas_nao_aderidas = (casas - casas_aderidas)
        self.quant_casas_equipadas = casas_equipadas
        self.quant_casas_nao_equipadas = casas_nao_equipadas
        if(casas!=0):
            self.porc_casas_aderidas = "%.2f" % (float(casas_aderidas)*100/float(casas))
            self.porc_casas_nao_aderidas = "%.2f" % (float(self.quant_casas_nao_aderidas)*100/float(casas))            
        else:
            self.porc_casas_aderidas = 0
            self.porc_casas_nao_aderidas = 0

        if(casas_aderidas!=0):
            self.porc_casas_equipadas = "%.2f" % (float(casas_equipadas)*100/float(casas_aderidas))
            self.porc_casas_nao_equipadas = "%.2f" % (float(self.quant_casas_nao_equipadas)*100/float(casas_aderidas))
        else:
            self.porc_casas_equipadas = 0
            self.porc_casas_nao_equipadas = 0

class RelatorioRegiaoTotal:
    def __init__(self,regiao,total,total_casas_aderidas,total_casas_equipadas,total_casas_nao_equipadas):
        self.regiao = regiao
        self.total = total
        self.total_casas_aderidas = total_casas_aderidas
        self.total_casas_nao_aderidas = (total - total_casas_aderidas)
        self.total_casas_equipadas = total_casas_equipadas
        self.total_casas_nao_equipadas = total_casas_nao_equipadas

        if(total!=0):
            self.porc_casas_aderidas = "%.2f" % (float(self.total_casas_aderidas)*100/float(total))
            self.porc_casas_nao_aderidas = "%.2f" % (float(self.total_casas_nao_aderidas)*100/float(total))            
        else:
            self.porc_casas_aderidas = 0
            self.porc_casas_nao_aderidas = 0

        if(total_casas_aderidas!=0):
            self.porc_casas_equipadas = "%.2f" % (float(self.total_casas_equipadas)*100/float(total_casas_aderidas))
            self.porc_casas_nao_equipadas = "%.2f" % (float(total_casas_nao_equipadas)*100/float(total_casas_aderidas))
        else:
            self.porc_casas_equipadas = 0
            self.porc_casas_nao_equipadas = 0

def report_regiao(request,regiao='NE'):

    REGIAO_CHOICES = {
        'SL': 'Sul',
        'SD': 'Sudeste',
        'CO': 'Centro-Oeste',
        'NE': 'Nordeste',
        'NO': 'Norte',
    }

    get_list_or_404(UnidadeFederativa,regiao=regiao)

    # Contando casas por estado
    estados = get_list_or_404(UnidadeFederativa,regiao=regiao)

    lista = []
    for estado in estados:

        casas = CasaLegislativa.objects.filter(municipio__uf=estado)
        casas_aderidas = casas.exclude(convenio=None).distinct()
        casas_equipadas = casas_aderidas.exclude(convenio__data_termo_aceite=None).distinct()
        casas_nao_equipadas = casas_aderidas.filter(convenio__data_termo_aceite=None).distinct()

        lista.append(
            RelatorioRegiao(
                estado.sigla,casas.count(),
                casas_aderidas.count(),
                casas_equipadas.count(),
                casas_nao_equipadas.count()
            )
        )

    # Total de casas na regiao
    casas = CasaLegislativa.objects.filter(municipio__uf__regiao=regiao)
    casas_aderidas = casas.exclude(convenio=None).distinct()
    casas_equipadas = casas_aderidas.exclude(convenio__data_termo_aceite=None).distinct()
    casas_nao_equipadas = casas_aderidas.filter(convenio__data_termo_aceite=None).distinct()
    sumario_regiao = RelatorioRegiaoTotal(
        REGIAO_CHOICES[regiao],
        casas.count(),
        casas_aderidas.count(),
        casas_equipadas.count(),
        casas_nao_equipadas.count(),
    )

#    response = HttpResponse(mimetype='application/pdf')
#    relatorio  = ConvenioReportRegiao(queryset=lista)
#    relatorio.generate_by(PDFGenerator, filename=response)
    
    data = datetime.datetime.now().strftime('%d/%m/%Y')
    hora = datetime.datetime.now().strftime('%H:%M')    
    pisa.showLogging()
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=RelatorioRegiao_' + regiao + '.pdf'
    t = loader.get_template('convenios/relatorio_por_regiao.html')
    c = Context({'lista': lista,'sumario_regiao':sumario_regiao,'data':data,'hora':hora})
    pdf = pisa.CreatePDF(t.render(c),response)
    if not pdf.err:
        pisa.startViewer(response)

    return response
     
