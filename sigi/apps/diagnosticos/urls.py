# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView
from sigi.apps.diagnosticos import views as diagnosticos_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Lista de Diagnósticos
    url(r'^mobile/$', diagnosticos_views.lista, name='lista_diagnosticos'),

    # Lista de Categorias
    url(r'^mobile/(?P<id_diagnostico>\d+)/categorias/$',
        diagnosticos_views.categorias, name='lista_categorias'),

    # Detalhes da Categoria da Casa Legislativa
    url(r'^mobile/(?P<id_diagnostico>\d+)/categorias/1/$',
        diagnosticos_views.categoria_casa_legislativa,
        name='detalhes_categoria_casa_legislativa'),

    # Detalhes da Categoria de Contatos
    url(r'^mobile/(?P<id_diagnostico>\d+)/categorias/2/$',
        diagnosticos_views.categoria_contatos,
        name='detalhes_categoria_contatos'),

    # Detalhes de Categorias Dinamicas
    url(r'^mobile/(?P<id_diagnostico>\d+)/categorias/(?P<id_categoria>\d+)/$',
        diagnosticos_views.categoria_detalhes, name='detalhes_categoria'),

    url(r'^mapa/$',
        TemplateView.as_view(template_name="diagnosticos/mapa.html"),
        name='template-mapa'),
    url(r'^mundiagjson/$', diagnosticos_views.municipios_diagnosticados,
        name='municipios-diagnosticados'),

    # Reports diagnosticos
    url(r'^diagnostico/(?P<id_diagnostico>\w+).pdf$',
        diagnosticos_views.diagnostico_pdf, name='diagnostico-pdf'),

    # Graficos de perguntas
    url(r'^graficos/$', diagnosticos_views.graficos,
        name="diagnosticos-graficos"),  # tagerror
    url(r'^api/$', diagnosticos_views.grafico_api,
        name="diagnosticos-grafico-api"),  # tagerror
]

urlpatterns += [
    # Login do Diagnóstico
    url(r'^mobile/login/$',
        auth_views.login, {'template_name':
                           'diagnosticos/diagnosticos_login.html'},
        name='login'),

    # Logout do Diagnóstico
    url(r'^mobile/logout/$', auth_views.logout,
        {'next_page': diagnosticos_views.LOGIN_REDIRECT_URL}, name='logout'),
]
