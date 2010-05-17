from django.http import HttpResponse, HttpResponseRedirect
from geraldo.generators import PDFGenerator
from sigi.apps.convenios.models import Convenio
from sigi.apps.convenios.reports import ConvenioReport

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
    report = ConvenioReport(queryset=qs)
    report.generate_by(PDFGenerator, filename=response)
    return response
