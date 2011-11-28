# -*- coding: utf8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    # Lista de Diagnósticos
    url(r'^$', 'sigi.apps.diagnosticos.views.lista', name='lista_diagnosticos'),

    # Lista de Categorias
    url(r'^(?P<id_diagnostico>\d+)/categorias/$', 'sigi.apps.diagnosticos.views.categorias', name='lista_categorias'),

    # Detalhes da Categoria
    url(r'^(?P<id_diagnostico>\d+)/categorias/(?P<id_categoria>\d+)/$',
        'sigi.apps.diagnosticos.views.categoria_detalhes',
        name='detalhes_categoria'),
)
