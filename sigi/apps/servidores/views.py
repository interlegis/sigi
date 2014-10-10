# -*- coding: utf-8 -*-

import new
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.db.models import Avg, Max, Min, Count
from sigi.apps.servidores.models import Servidor, Funcao
from sigi.shortcuts import render_to_pdf


def servidores_por_funcao(request):
    report = Funcao.objects.values('funcao').annotate(funcao__count=Count('funcao')).order_by('funcao__count')
    total = Funcao.objects.count()

    context = RequestContext(request, {
        'pagesize': 'A4',
        'report': report,
        'total': total
    })

    return render_to_pdf('servidores/servidores_por_funcao.html', context)


def servidores_por_cargo(request):
    report = Funcao.objects.values('cargo').annotate(cargo__count=Count('cargo')).order_by('cargo__count')
    total = Funcao.objects.count()

    context = RequestContext(request, {
        'pagesize': 'A4',
        'report': report,
        'total': total
    })

    return render_to_pdf('servidores/servidores_por_cargo.html', context)
