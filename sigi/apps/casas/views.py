# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from geraldo.generators import PDFGenerator
from sigi.apps.casas.models import CasaLegislativa

from sigi.apps.casas.reports import CasasLegislativasLabels
from sigi.apps.casas.reports import CasasLegislativasLabelsSemPresidente
from sigi.apps.casas.reports import CasasLegislativasReport
from sigi.apps.casas.reports import CasasSemConvenioReport
from sigi.apps.casas.reports import InfoCasaLegislativa

import csv

def query_ordena(qs,o,ot):
    list_display = ('nome','municipio','presidente','logradouro')

    aux = list_display[(int(o)-1)]
    if ot =='asc':
        qs = qs.order_by(aux)
    else:
        qs = qs.order_by("-"+aux)
    return qs

def get_for_qs(get,qs):
    kwargs = {}
    for k,v in get.iteritems():
        if not k == 'o':
            if k == "ot":
                qs = query_ordena(qs,get["o"],get["ot"])
            else:
                kwargs[str(k)] = v
                qs = qs.filter(**kwargs)
    return qs


def labels_report(request, id=None,queryset=None):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """    
    if queryset:
        qs = queryset
    else:
        qs = CasaLegislativa.objects.all()
        if id:
            qs = qs.filter(pk=id)
        elif request.GET:
            qs = get_for_qs(request.GET,qs)

    response = HttpResponse(mimetype='application/pdf')
    report = CasasLegislativasLabels(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)

    return response

def labels_report_sem_presidente(request, id=None,queryset=None):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """
    if queryset:
        qs = queryset
    else:
        qs = CasaLegislativa.objects.all()
        if id:
            qs = qs.filter(pk=id)
        elif request.GET:
            qs = get_for_qs(request.GET,qs)

    response = HttpResponse(mimetype='application/pdf')
    report = CasasLegislativasLabelsSemPresidente(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)

    return response


def report(request, id=None,queryset=None):
    if queryset:
        qs = queryset
    else:
        qs = CasaLegislativa.objects.all()
        if id:
            qs = qs.filter(pk=id)
        elif request.GET:
            qs = get_for_qs(request.GET,qs)

        if not qs:
            return HttpResponseRedirect('../')
    
    #qs.order_by('municipio__uf','nome')
    response = HttpResponse(mimetype='application/pdf')
    report = CasasLegislativasReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response

def casa_info(request,id=None,queryset=None):
    if queryset:
        qs = queryset
    else:
        qs = CasaLegislativa.objects.all()
        if id:
            qs = qs.filter(pk=id)
        elif request.GET:
            qs = get_for_qs(request.GET,qs)
    if not qs:
        return HttpResponseRedirect('../')

    response = HttpResponse(mimetype='application/pdf')   

    # Gera um relatorio para cada casa e concatena os relatorios
    cont = 0
    canvas = None    
    quant = qs.count()    
    if quant > 1:    
        for i in qs:
            cont += 1
            #queryset deve ser uma lista
            lista = (i,)
            if cont == 1:
                report = InfoCasaLegislativa(queryset=lista)
                canvas = report.generate_by(PDFGenerator, return_canvas=True,filename=response,)
            else:
                report = InfoCasaLegislativa(queryset=lista)
                if cont == quant:
                    report.generate_by(PDFGenerator, canvas=canvas)
                else:
                    canvas = report.generate_by(PDFGenerator, canvas=canvas, return_canvas=True)
    else:
        report = InfoCasaLegislativa(queryset=qs)
        report.generate_by(PDFGenerator,filename=response)
    
    return response

def casas_sem_convenio_report(request):
    qs = CasaLegislativa.objects.filter(convenio=None).order_by('municipio__uf','nome')
    
    if request.GET:
        qs = get_for_qs(request.GET,qs)
    if not qs:
        return HttpResponseRedirect('../')
    
    response = HttpResponse(mimetype='application/pdf')
    report = CasasSemConvenioReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response



def export_csv(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=casas.csv'
    
    csv_writer = csv.writer(response)
    casas = CasaLegislativa.objects.all()
    for casa in casas:
        csv_writer.writerow([casa.nome.encode("utf-8"), casa.municipio.uf.sigla.encode("utf-8")])
    
    return response
