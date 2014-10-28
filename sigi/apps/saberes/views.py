# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.db.models import Count
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from sigi.apps.mdl.models import User, CourseStatus
from sigi.apps.saberes.models import CategoriasInteresse

def dashboard(request):
    areas = []
    numeros = [
        {'descricao': _(u'Total de usuários cadastrados'), 'valor': User.objects.count()},
        {'descricao': _(u'Novos usuários cadastrados')   , 'valor': User.objects.filter(firstaccess__gte=1392326052).count()}
    ]
    
    for ci in CategoriasInteresse.objects.all():
        matriculas = ci.total_alunos()
        numeros.append({'descricao': _(u'Total de matrículas em %s' % ci.descricao.lower()), 'valor': matriculas})
        area = {'titulo': ci.descricao, 'dados': [{'descricao': _(u'Total de matrículas'), 'valor': matriculas}]}
        for course in ci.get_all_courses(only_visible=True):
            area['dados'].append({'descricao': course.fullname, 'valor': course.total_alunos()})
#         if ci.apurar_alunos: # Apurar número de alunos
#             valor = sum([curso.total_ativos() for curso in ci.get_all_courses()])
#             area['dados'].append({'descricao': _(u'Total de alunos aceitos'), 'valor': valor})
#         if ci.apurar_conclusao:
#             cl = [curso.id for curso in ci.get_all_courses()]
#             for cs in CourseStatus.objects.filter(courseid__in=cl).values('status').annotate(valor=Count('userid')):
#                 area['dados'].append({'descricao': cs['status'], 'valor': cs['valor']})
#                  
        areas.append(area)
        
    paineis = [{'titulo': _(u'Saberes em números'), 'dados': numeros}] + areas
    
    
    totais = []
    
#     for i in MapaCategorias.INTERESSE_CHOICES:
#         totais.append({'nome': i[1], 'total_turmas': '', 'total_alunos': '', 'padding': 0})
#         for mapa in MapaCategorias.objects.filter(area_interesse=i[0]):
#             totais.append({'nome': mapa.categoria.name, 'total_turmas': mapa.total_turmas(), 'total_alunos': mapa.total_alunos(), 'padding': 1})
#             for c in mapa.categoria.children.all():
#                 totais.append({'nome': c.name, 'total_turmas': c.total_turmas(), 'total_alunos': c.total_alunos(), 'padding': 2})
                
    tutorias = []
    
#     for mapa in MapaCategorias.objects.filter(area_interesse='CT'):
#         tutorias.append({'nome': mapa.categoria.name, 'inscritos': mapa.total_alunos(), 'padding': 0})
#         for c in mapa.categoria.courses.all():
#             tutorias.append({'nome': c.fullname, 'inscritos': c.total_alunos(), 'padding': 1})
            
    extra_context = {'numeros': numeros, 'paineis': paineis, 'totais': totais, 'tutorias': tutorias}
    
    return render_to_response('saberes/dashboard.html', extra_context, context_instance=RequestContext(request))