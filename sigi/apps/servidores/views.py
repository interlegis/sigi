# -*- coding: utf-8 -*-

import new

from django.db.models import Avg, Count, Max, Min
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext

from sigi.apps.servidores.models import Funcao, Servidor
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
