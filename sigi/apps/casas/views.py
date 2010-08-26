# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from geraldo.generators import PDFGenerator
from sigi.apps.casas.models import CasaLegislativa

from sigi.apps.casas.reports import CasasLegislativasLabels
from sigi.apps.casas.reports import CasasLabelsNomeMaior
from sigi.apps.casas.reports import CasasLabelsEnderecoMaior
from sigi.apps.casas.reports import CasasLabelsNomeMaiorEnderecoMaior

from sigi.apps.casas.reports import CasasLegislativasReport
from sigi.apps.casas.reports import CasasSemConvenioReport
from sigi.apps.casas.reports import InfoCasaLegislativa
import csv

from sigi.apps.casas.reports import string_to_cm
from reportlab.lib.units import cm


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
            kwargs = {}
            for k, v in request.GET.iteritems():
                kwargs[str(k)] = v
                qs = qs.filter(**kwargs)
  

    casasNormais = []
    casasNomesGrandes = []
    casasEnderecoGrande = []
    casasNomeEnderecoGrande = []
    tamanho = 8.2
    for casa in qs:
        tamNome = string_to_cm("Presidente da " + casa.nome)
        tamEnder = string_to_cm((casa.logradouro +" - "+ casa.bairro)
                            if len(casa.bairro) != 0
                            else casa.logradouro
        )
        if tamNome <tamanho and tamEnder <tamanho:
            casasNormais.append(casa)
        elif tamNome <tamanho and tamEnder > tamanho:
            casasEnderecoGrande.append(casa)
        elif tamNome >tamanho and tamEnder < tamanho:
            casasNomesGrandes.append(casa)
        else:
            casasNomeEnderecoGrande.append(casa)

    response = HttpResponse(mimetype='application/pdf')

    cN    = len(casasNormais)
    cNoG  = len(casasNomesGrandes)
    cEG   = len(casasEnderecoGrande)
    cNoEG = len(casasNomeEnderecoGrande)

    # Testando se as listas não estão vazias e criando os reports
    report1=report2=report3=report4=None
    canvas = None
    if cN:
        report1 = CasasLegislativasLabels(queryset=casasNormais)
        if cNoG or cEG or cNoEG:
            canvas = report1.generate_by(
                PDFGenerator,
                filename=response,return_canvas=True,
            )
        else:
            report1.generate_by(PDFGenerator, filename=response)

    if cNoG:
        report2 = CasasLabelsNomeMaior(queryset=casasNomesGrandes)
        if cEG or cNoEG:
            if canvas:
                canvas = report2.generate_by(
                    PDFGenerator,
                    canvas=canvas,
                    return_canvas=True,
                )
            else:
                canvas = report2.generate_by(
                    PDFGenerator,
                    canvas=canvas,
                    return_canvas=True,
                    filename=response,
                )
        else:
            if canvas:
                report2.generate_by(
                    PDFGenerator,
                    canvas=canvas,                    
                )
            else:
                report2.generate_by(PDFGenerator, filename=response)

    if cEG:
        report3 = CasasLabelsEnderecoMaior(queryset=casasEnderecoGrande)
        if cNoEG:
            if canvas:
                canvas = report3.generate_by(
                    PDFGenerator,
                    canvas=canvas,
                    return_canvas=True,
                )
            else:
                canvas = report3.generate_by(
                    PDFGenerator,
                    canvas=canvas,
                    return_canvas=True,
                    filename=response,
                )
        else:
             if canvas:
                 report3.generate_by(
                     PDFGenerator,
                     canvas=canvas,
                 )
             else:
                 report3.generate_by(PDFGenerator, filename=response)


    if cNoEG:
        report4 = CasasLabelsNomeMaiorEnderecoMaior(queryset=casasNomeEnderecoGrande)
        if canvas:
            report4.generate_by(
                PDFGenerator,
                canvas=canvas,
            )
        else:
            report4.generate_by(PDFGenerator, filename=response)

    return response

def report(request, id=None):
    qs = CasaLegislativa.objects.all().order_by('municipio__uf','nome')
    if id:
        qs = qs.filter(pk=id)
    elif request.GET:
        kwargs = {}
        for k, v in request.GET.iteritems():
            kwargs[str(k)] = v
            qs = qs.filter(**kwargs)
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
            kwargs = {}
            for k, v in request.GET.iteritems():
                kwargs[str(k)] = v
                qs = qs.filter(**kwargs)
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
        kwargs = {}
        for k, v in request.GET.iteritems():
            kwargs[str(k)] = v
            qs = qs.filter(**kwargs)
    if not qs:
        return HttpResponseRedirect('../')

    #qs.order_by('municipio__uf','nome')
    response = HttpResponse(mimetype='application/pdf')
    report = CasasSemConvenioReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response



def export_csv(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=casas.csv'
    
    csv_writer = csv.writer(response)
    casas = CasaLegislativa.objects.filter(municipio__uf__sigla=u'MG')
    for casa in casas:
        csv_writer.writerow([casa.nome.encode("utf-8"), casa.municipio.uf.sigla.encode("utf-8")])
    
    return response
