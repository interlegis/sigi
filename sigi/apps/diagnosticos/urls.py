# -*- coding: utf8 -*-
from django.conf.urls.defaults import patterns, url

LOGOUT_REDIRECT_URL = '/mobile/diagnosticos/login'

urlpatterns = patterns('',
    # Lista de Diagnósticos
    url(r'^$', 'sigi.apps.diagnosticos.views.lista', name='lista_diagnosticos'),

    # Login do Diagnóstico
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':
        'diagnosticos/diagnosticos_login.html'}, name='login'),

    # Logout do Diagnóstico
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': LOGOUT_REDIRECT_URL}, name='logout'),

    # Lista de Categorias
    url(r'^(?P<id_diagnostico>\d+)/categorias/$', 'sigi.apps.diagnosticos.views.categorias', name='lista_categorias'),

    # Detalhes da Categoria
    url(r'^(?P<id_diagnostico>\d+)/categorias/(?P<id_categoria>\d+)/$',
        'sigi.apps.diagnosticos.views.categoria_detalhes',
        name='detalhes_categoria'),
)
