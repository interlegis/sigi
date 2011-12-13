# -*- coding: utf8 -*-
from django.conf.urls.defaults import patterns, url

LOGIN_REDIRECT_URL = '/sigi/mobile/diagnosticos/login'

urlpatterns = patterns('',
    # Lista de Diagnósticos
    url(r'^$', 'sigi.apps.diagnosticos.views.lista', name='lista_diagnosticos'),

    # Login do Diagnóstico
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':
        'diagnosticos/diagnosticos_login.html'}, name='login'),

    # Logout do Diagnóstico
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': LOGIN_REDIRECT_URL}, name='logout'),

    # Lista de Categorias
    url(r'^(?P<id_diagnostico>\d+)/categorias/$', 'sigi.apps.diagnosticos.views.categorias', name='lista_categorias'),

    # Detalhes da Categoria da Casa Legislativa
    url(r'^(?P<id_diagnostico>\d+)/categorias/1/$',
        'sigi.apps.diagnosticos.views.categoria_casa_legislativa',
        name='detalhes_categoria_casa_legislativa'),

    # Detalhes da Categoria de Contatos
    url(r'^(?P<id_diagnostico>\d+)/categorias/2/$',
        'sigi.apps.diagnosticos.views.categoria_contatos',
        name='detalhes_categoria_contatos'),

    # Detalhes de Categorias Dinamicas
    url(r'^(?P<id_diagnostico>\d+)/categorias/(?P<id_categoria>\d+)/$',
        'sigi.apps.diagnosticos.views.categoria_detalhes',
        name='detalhes_categoria'),
)
