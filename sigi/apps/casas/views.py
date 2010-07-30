from django.http import HttpResponse, HttpResponseRedirect
from geraldo.generators import PDFGenerator
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.casas.reports import CasasLegislativasLabels
from sigi.apps.casas.reports import CasasLegislativasReport


def labels_report(request, id=None):
    """ TODO: adicionar suporte para resultado de pesquisa do admin.
    """
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
    report = CasasLegislativasLabels(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
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

def casas_sem_convenio_report(request):
    qs = CasaLegislativa.objects.filter(convenio=None).order_by('municipio__uf','nome')

    response = HttpResponse(mimetype='application/pdf')
    report = CasasLegislativasReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response
