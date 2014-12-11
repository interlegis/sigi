# -*- coding: utf-8 -*-

from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.db.models import Sum, Avg
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from sigi.apps.mdl.models import User, CourseStats
from sigi.apps.saberes.models import CategoriasInteresse, PainelItem

def dashboard(request):
    paineis = OrderedDict()
    
    for p in PainelItem.objects.all():
        if p.painel not in paineis:
            paineis[p.painel] = {'titulo': p.painel, 'dados': []}
        paineis[p.painel]['dados'].append(p)
    
    extra_context = {'paineis': paineis}
    
    return render_to_response('saberes/dashboard.html', extra_context, context_instance=RequestContext(request))