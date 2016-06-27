# coding: utf-8
from django.conf.urls import patterns, url

from .views import (cursos_com_tutoria, cursos_sem_tutoria, dashboard,
                    pentaho_proxy)

urlpatterns = patterns(
    'sigi.apps.saberes.views',

    url(r'^dashboard/cursos-sem-turoria/?$', cursos_sem_tutoria, name="saberes-cursos-sem-tutoria"),
    url(r'^dashboard/cursos-com-turoria/?$', cursos_com_tutoria, name="saberes-cursos-com-tutoria"),
    url(r'^dashboard/?$', dashboard, name="saberes-dashboard-view"),
    url(r'^(?P<path>(plugin|api)/.*)$', pentaho_proxy),
)
