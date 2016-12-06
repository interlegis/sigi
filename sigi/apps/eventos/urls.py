# coding: utf-8
from django.conf.urls import url
from sigi.apps.eventos import views

urlpatterns = [
    # Painel de ocorrencias
    url(r'^calendario/$', views.calendario, name='eventos-calendario'),
    url(r'^alocacaoequipe/$', views.alocacao_equipe, name='eventos-alocacaoequipe'),
]
