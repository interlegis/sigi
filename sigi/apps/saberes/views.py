# -*- coding: utf-8 -*-
import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth

from sigi.settings import (PENTAHO_DASHBOARDS, PENTAHO_SERVER,
                           PENTAHO_USERNAME_PASSWORD)

PENTAHO_CDF_URL = 'http://%s/pentaho/plugin/pentaho-cdf-dd/api/renderer/' % PENTAHO_SERVER


def get_dashboard_parts(dashboard_id, this_host):
    params = PENTAHO_DASHBOARDS[dashboard_id]
    params['root'] = this_host
    return [requests.get(PENTAHO_CDF_URL + method,
                         params=params, auth=HTTPBasicAuth(*PENTAHO_USERNAME_PASSWORD)).content
            for method in ('getHeaders', 'getContent')]


def make_dashboard(dashboard_id, adjust_content=lambda x: x):
    def view(request):
        headers, content = get_dashboard_parts(dashboard_id, request.META['HTTP_HOST'])
        if request.is_secure:
            headers = headers.replace('http://', 'https://')
        content = adjust_content(content)
        return render(request, 'saberes/dashboard.html',
                      dict(headers=headers, content=content))
    return view


def use_to_container_fluid(content):
    return content.replace("class='container'", "class='container-fluid'")


dashboard = make_dashboard('saberes-geral')
cursos_sem_tutoria = make_dashboard('saberes-cursos-sem-tutoria', use_to_container_fluid)
cursos_com_tutoria = make_dashboard('saberes-cursos-com-tutoria', use_to_container_fluid)


@csrf_exempt
def pentaho_proxy(request, path):
    url = 'http://%s/pentaho/%s' % (PENTAHO_SERVER, path)
    params = request.GET or request.POST
    auth = HTTPBasicAuth(*PENTAHO_USERNAME_PASSWORD)
    response = requests.get(url, params=params, auth=auth)
    return HttpResponse(response.content,
                        status=response.status_code,
                        content_type=response.headers.get('Content-Type'))
