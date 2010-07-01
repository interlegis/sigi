from django.http import HttpResponse, HttpResponseRedirect
from geraldo.generators import PDFGenerator
from sigi.apps.convenios.models import Convenio
from sigi.apps.convenios.reports import ConvenioReport, ConvenioReportRegiao
from sigi.apps.casas.models import CasaLegislativa


def report(request, id=None):
    qs = Convenio.objects.all()
    if id:
        qs = qs.filter(pk=id)
    elif request.GET: #Se tiver algum parametro de pesquisa
        kwargs = {}
        ids = 0
        for k, v in request.GET.iteritems():
            kwargs[str(k)] = v
            if(str(k)=='ids'):
                ids = 1
                break
            qs = qs.filter(**kwargs)
        if ids:
            query = 'id IN ('+ kwargs['ids'].__str__()+')'
            qs = Convenio.objects.extra(where=[query])
    if not qs:
        return HttpResponseRedirect('../')
    response = HttpResponse(mimetype='application/pdf')
    report = ConvenioReport(queryset=qs.order_by('casa_legislativa'))
    report.generate_by(PDFGenerator, filename=response)
    return response

class Relatorios(object):
    def __init__(self, regiao, casas, casas_conveniadas):
        self.regiao = regiao
        self.casas = casas
        self.casas_conveniadas = casas_conveniadas
        if(casas_conveniadas!=0):
            self.porc_casas_conveniadas = float(casas_conveniadas)/float(casas)*100
        else:
            self.porc_casas_conveniadas = 0

def reportRegiao(request):
    REGIAO_CHOICES = (
        ('SL', 'Sul'),
        ('SD', 'Sudeste'),
        ('CO', 'Centro-Oeste'),
        ('NE', 'Nordeste'),
        ('NO', 'Norte'),
    )
    relatorio = []
    for casa in REGIAO_CHOICES:
        casasSD = CasaLegislativa.objects.filter(municipio__uf__regiao=casa[0])
        casasConvSD = CasaLegislativa.objects.filter(convenio__casa_legislativa__municipio__uf__regiao=casa[0]).distinct()

        relatorio.append(Relatorios(casa[1], casasSD.count(), 
                                casasConvSD.count()))
    
    response = HttpResponse(mimetype='application/pdf')
    relatorio  = ConvenioReportRegiao(queryset=relatorio)
    relatorio.generate_by(PDFGenerator, filename=response)
    return response
     
