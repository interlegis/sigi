# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'sigi.apps.eventos.views',
    # Painel de ocorrencias
    url(r'^calendario/$', 'calendario', name='eventos-calendario'),
    url(r'^alocacaoequipe/$', 'alocacao_equipe', name='eventos-alocacaoequipe'),
)
