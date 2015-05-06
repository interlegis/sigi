# -*- coding: utf-8 -*-
from collections import OrderedDict

import requests
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth

from sigi.apps.mdl.models import CourseStats
from sigi.apps.saberes.models import CategoriasInteresse
from sigi.settings import PENTAHO_SERVER, PENTAHO_DASHBOARDS, PENTAHO_USERNAME_PASSWORD


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


def detail(request, area):
    ci = get_object_or_404(CategoriasInteresse, pk=area)

    head_flags = []
    table_data = OrderedDict()

    for c in CourseStats.objects.filter(category__in=ci.categorias(subcategorias=True)).order_by('course__fullname'):
        if c.course_id not in table_data:
            table_data[c.course_id] = {'course_name': c.course.fullname, 'total_matriculas': 0}

        table_data[c.course_id]['total_matriculas'] += c.usercount
        table_data[c.course_id][c.completionstatus] = c.usercount

        head_flags.append(c.completionstatus)

        if c.completionstatus == 'A':
            table_data[c.course_id]['media_aprovados'] = c.gradeaverage
            head_flags.append('MA')

        if c.completionstatus == 'R':
            table_data[c.course_id]['media_reprovados'] = c.gradeaverage
            head_flags.append('MR')

    head_flags = set(head_flags)
    table_head = [_(u'Curso / turma'), _(u'Total de matrículas')]

    if 'N' in head_flags:
        table_head.append(_(u'Matrículas rejeitadas'))
        table_head.append(_(u'Alunos efetivos'))
        for k in table_data:
            table_data[k]['efetivos'] = table_data[k]['total_matriculas'] - (table_data[k]['N'] if 'N' in table_data[k] else 0)

    if 'C' in head_flags:
        table_head.append(_(u'Em curso'))
    if 'L' in head_flags:
        table_head.append(_(u'Abandono'))
    if 'R' in head_flags:
        table_head.append(_(u'Reprovação'))
    if 'A' in head_flags:
        table_head.append(_(u'Aprovação'))
    if 'MA' in head_flags:
        table_head.append(_(u'Média das notas dos alunos aprovados'))
    if 'MR' in head_flags:
        table_head.append(_(u'Média das notas dos alunos reprovados'))

    extra_context = {'area': ci, 'table_head': table_head, 'table_data': table_data, 'flags': head_flags}
    return render_to_response('saberes/detail.html', extra_context, context_instance=RequestContext(request))
