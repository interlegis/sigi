# -*- coding: utf-8 -*-
'''
Created on 11/05/2011

@author: sesostris
'''
from django.shortcuts import render_to_response
from birtReport.birtReportTree import BirtReportTree
from birtReport.birtReport import BirtReport
from settings import BASE_DIR
from django.http import HttpResponse, Http404, HttpResponseServerError
import os

BIRT_REPORT_DIR = BASE_DIR + '/BIRT_Reports/'

def menu(request, folder = ''):
    brt   = BirtReportTree(BIRT_REPORT_DIR)
    
    if folder == '':
        items = brt.getRootItems()
    else:
        folder = folder + '/'
        items = brt.getFolderItems(folder)
        
    folders = items['folders']
    reports = items['reports']
    return render_to_response('birt/birtMenu.html', {'folders': folders, 'reports': reports, 'submenu': folder})

def run(request, file):
    birt   = BirtReport(BIRT_REPORT_DIR + file)
    params = birt.getReportParams()
    
    if params != {}:
        return render_to_response('birt/birtForm.html', {'birt': birt, 'params': params})
    
    return HttpResponse('<html><body>Deu a louca ' + str(params) + '</body></html>')

def show(request):
    if not request.POST.has_key('reportFileName'):
        raise Http404
    
    rptFileName = request.POST['reportFileName']
    birt        = BirtReport(rptFileName)
    
    if not birt.rptExists():
        raise Http404
    
    if os.environ.has_key('BIRT_HOME'):
        birt_home = os.environ['BIRT_HOME']
    else:
        return HttpResponseServerError('Serviço não instalado ou indisponível.')
    
    params = ''
    
    for pName in birt.getReportParams():
        if request.POST.has_key(pName):
            params += '"%s=%s" ' % (pName, request.POST[pName])
        else:
            params += '"%s=%s" ' % (pName, '')

    output   = os.tempnam()
    fileName = os.path.split(rptFileName)[1]
    fileName = os.path.splitext(fileName)[0]

    if (request.POST['submit'] == 'Ver na tela'):
        format   = 'HTML'
        mimeType = 'text/html'
        contentDisposition = ''
    else:
        format = 'PDF'
        mimeType = 'application/pdf'
        contentDisposition = 'attachment; filename=%s.pdf' % fileName

    fileName = output + '/' + fileName + '.' + format
    
    cmd = '%s/ReportEngine/genReport.sh -f %s -p %s -o %s %s' % (birt_home, format, params, output, rptFileName)
    os.system(cmd)
    
    if not os.path.isfile(fileName):
        return HttpResponseServerError('Servidor não conseguiu produzir o relatório: %s' % fileName)
    
    resultFile = open(fileName)
    result     = resultFile.read()
    resultFile.close()
    
    response = HttpResponse(mimetype=mimeType)
    response['Content-Disposition'] = contentDisposition
    response.write(result)
              
    return response