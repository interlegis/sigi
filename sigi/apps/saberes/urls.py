# coding: utf-8
from django.conf.urls import url
from sigi.apps.saberes.views import cursos_sem_tutoria, cursos_com_tutoria, dashboard, pentaho_proxy


urlpatterns = [
    url(r'^dashboard/cursos-sem-turoria/?$', cursos_sem_tutoria, name="saberes-cursos-sem-tutoria"),
    url(r'^dashboard/cursos-com-turoria/?$', cursos_com_tutoria, name="saberes-cursos-com-tutoria"),
    url(r'^dashboard/?$', dashboard, name="saberes-dashboard-view"),
    url(r'^(?P<path>(plugin|api)/.*)$', pentaho_proxy),
]
