# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

LOGIN_REDIRECT_URL = '/diagnosticos/mobile/login'

urlpatterns = patterns(
    'sigi.apps.diagnosticos.views',

    # Lista de Diagnósticos
    url(r'^mobile/$', 'lista', name='lista_diagnosticos'),

    # Lista de Categorias
    url(r'^mobile/(?P<id_diagnostico>\d+)/categorias/$',
        'categorias', name='lista_categorias'),

    # Detalhes da Categoria da Casa Legislativa
    url(r'^mobile/(?P<id_diagnostico>\d+)/categorias/1/$',
        'categoria_casa_legislativa', name='detalhes_categoria_casa_legislativa'),

    # Detalhes da Categoria de Contatos
    url(r'^mobile/(?P<id_diagnostico>\d+)/categorias/2/$',
        'categoria_contatos', name='detalhes_categoria_contatos'),

    # Detalhes de Categorias Dinamicas
    url(r'^mobile/(?P<id_diagnostico>\d+)/categorias/(?P<id_categoria>\d+)/$',
        'categoria_detalhes', name='detalhes_categoria'),

    url(r'^mapa/$', TemplateView.as_view(template_name="diagnosticos/mapa.html"), name='template-mapa'),
    url(r'^mundiagjson/$', 'municipios_diagnosticados', name='municipios-diagnosticados'),

    # Reports diagnosticos
    url(r'^diagnostico/(?P<id_diagnostico>\w+).pdf$', 'diagnostico_pdf', name='diagnostico-pdf'),

    # Graficos de perguntas
    url(r'^graficos/$', 'graficos', name="diagnosticos-graficos"),  # tagerror
    url(r'^api/$', 'grafico_api', name="diagnosticos-grafico-api"),  # tagerror

)

urlpatterns += patterns(
    'django.contrib.auth.views',

    # Login do Diagnóstico
    url(r'^mobile/login/$', 'login', {'template_name':
                                      'diagnosticos/diagnosticos_login.html'}, name='login'),

    # Logout do Diagnóstico
    url(r'^mobile/logout/$', 'logout',
        {'next_page': LOGIN_REDIRECT_URL}, name='logout'),
)
