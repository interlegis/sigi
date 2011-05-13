# -*- coding: utf-8 -*-
'''
Created on 11/05/2011

@author: sesostris
'''
from django.shortcuts import render_to_response
from birtReport.birtReportTree import BirtReportTree
from birtReport.birtReport import BirtReport
from settings import BASE_DIR
from django.http import HttpResponse, QueryDict, Http404

BIRT_REPORT_DIR = BASE_DIR + '/BIRT_Reports/'

def menu(request, folder = ''):
    brt   = BirtReportTree(BIRT_REPORT_DIR)
    
    if folder == '':
        items = brt.getRootItems()
    else:
        items = brt.getFolderItems(folder)
        
    folders = items['folders']
    reports = items['reports']
    return render_to_response('birt/birtMenu.html', {'folders': folders, 'reports': reports, 'submenu': folder})

def run(request, file):
    birt   = BirtReport(BIRT_REPORT_DIR + file + '.rptdesign')
    params = birt.getReportParams()
    
    if params != {}:
        return render_to_response('birt/birtForm.html', {'birt': birt, 'params': params})
    
    return HttpResponse('<html><body>Deu a louca ' + str(params) + '</body></html>')

def show(request):
#    QueryDict.has_key(k)
    html  = '<html><body><h1>Vejamos o que dá pra fazer...</h1>'
    if not request.POST.has_key('reportFileName'):
        raise Http404
    
    rptFileName = request.POST['reportFileName']
    birt        = BirtReport(rptFileName)
    
    if not birt.rptExists():
        raise Http404
    
    params = {}
    
    for pName in birt.getReportParams():
        if request.POST.has_key(pName):
            params[pName] = request.POST[pName]
        else:
            params[pName] = '' 
            
    html += '<p>%s</p>' % str(params)

    html += '</body></html>'
    return HttpResponse(html)