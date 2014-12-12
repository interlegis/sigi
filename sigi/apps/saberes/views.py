# -*- coding: utf-8 -*-

from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.db.models import Sum, Avg
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from sigi.apps.mdl.models import User, CourseStats
from sigi.apps.saberes.models import CategoriasInteresse, PainelItem

def dashboard(request):
    paineis = OrderedDict()
    
    for p in PainelItem.objects.all():
        if p.painel not in paineis:
            paineis[p.painel] = {'titulo': p.painel, 'dados': []}
        paineis[p.painel]['dados'].append(p)
        
    for p in paineis:
        try:
            paineis[p]['area'] = CategoriasInteresse.objects.get(descricao=paineis[p]['titulo'])
        except:
            pass 
    
    extra_context = {'paineis': paineis}
    
    return render_to_response('saberes/dashboard.html', extra_context, context_instance=RequestContext(request))

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
    