# coding: utf-8
from django.conf.urls import url
from sigi.apps.saberes import views


urlpatterns = [
    url(r'^dashboard/cursos-sem-turoria/?$', views.cursos_sem_tutoria, name="saberes-cursos-sem-tutoria"),
    url(r'^dashboard/cursos-com-turoria/?$', views.cursos_com_tutoria, name="saberes-cursos-com-tutoria"),
    url(r'^dashboard/?$', views.dashboard, name="saberes-dashboard-view"),
    url(r'^(?P<path>(plugin|api)/.*)$', views.pentaho_proxy),
]
