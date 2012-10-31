#-*- coding:utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to, direct_to_template 
import sites

# register admin filters
import admin.filterspecs

urlpatterns = patterns(
    '',

    ('^$', redirect_to, {'url': '/sigi/'}),

    # Diagnosticos
    (r'^sigi/mobile/diagnosticos/', include('sigi.apps.diagnosticos.urls')),
    (r'^sigi/diagnosticos/mapa/$', direct_to_template, {'template': 'diagnosticos/mapa.html'}),
    (r'^sigi/diagnosticos/mundiagjson/$', 'sigi.apps.diagnosticos.views.municipios_diagnosticados'),
    

    # Informacoes de uma casa legislativa
    (r'^sigi/casas/casalegislativa/(?P<id>\w+)/report_complete/',
     'sigi.apps.casas.views.report_complete'),
    (r'^sigi/casas/casalegislativa/report_complete/',
     'sigi.apps.casas.views.report_complete'),
    # reports labels
    (r'^sigi/casas/casalegislativa/labels/',
     'sigi.apps.casas.views.labels_report'),
    (r'^sigi/casas/casalegislativa/(?P<id>\w+)/labels/',
     'sigi.apps.casas.views.labels_report'),
    # reports labels sem presidente
    (r'^sigi/casas/casalegislativa/labels_sem_presidente/',
     'sigi.apps.casas.views.labels_report_sem_presidente'),
    (r'^sigi/casas/casalegislativa/(?P<id>\w+)/labels_sem_presidente/',
     'sigi.apps.casas.views.labels_report_sem_presidente'),
    # reports casa    
    (r'^sigi/casas/casalegislativa/reports/',
    'sigi.apps.casas.views.report'),    
    (r'^sigi/casas/casalegislativa/casas_sem_convenio_report/',
    'sigi.apps.casas.views.casas_sem_convenio_report'),
    # reports convenios
    (r'^sigi/convenios/convenio/reports/',
     'sigi.apps.convenios.views.report'),
    # reports diagnosticos
    (r'^sigi/diagnosticos/diagnostico/(?P<id_diagnostico>\w+).pdf',
     'sigi.apps.diagnosticos.views.diagnostico_pdf'),
    # reports servidores
    (r'^sigi/servidores/servidores_por_funcao.pdf',
     'sigi.apps.servidores.views.servidores_por_funcao'),
    (r'^sigi/servidores/servidores_por_cargo.pdf',
     'sigi.apps.servidores.views.servidores_por_cargo'),
    #Carrinho Casa
    (r'^sigi/casas/casalegislativa/carrinho/deleta_itens_carrinho',
     'sigi.apps.casas.views.deleta_itens_carrinho'),
    (r'^sigi/casas/casalegislativa/carrinho/excluir_carrinho',
     'sigi.apps.casas.views.excluir_carrinho'),
    (r'^sigi/casas/casalegislativa/carrinho/',
     'sigi.apps.casas.views.visualizar_carrinho'),
    #Carrinho Convenio
    (r'^sigi/convenios/convenio/carrinho/deleta_itens_carrinho',
     'sigi.apps.convenios.views.deleta_itens_carrinho'),
    (r'^sigi/convenios/convenio/carrinho/excluir_carrinho',
     'sigi.apps.convenios.views.excluir_carrinho'),
    (r'^sigi/convenios/convenio/carrinho/',
     'sigi.apps.convenios.views.visualizar_carrinho'),
    #CSV Casa
    (r'^sigi/casas/casalegislativa/csv/',
     'sigi.apps.casas.views.export_csv'),
    #CSV Convenio
    (r'^sigi/convenios/convenio/csv/',
    'sigi.apps.convenios.views.export_csv'),
    # Resumo por região PDF     
    (r'^sigi/reportsRegiao/(?P<regiao>\w+)',
     'sigi.apps.convenios.views.report_regiao'),
    # Submenu com Birt reports
    (r'^sigi/birt/menu/(?P<folder>\w+)',
     'sigi.apps.birt.views.menu'),
    # Execução com Birt reports
    (r'^sigi/birt/run/(?P<file>.+)',
     'sigi.apps.birt.views.run'),
    # Mostrar um relatório em formato HTML
    (r'^sigi/birt/showreport/',
     'sigi.apps.birt.views.show'),
    # Menu com Birt reports
    (r'^sigi/birt/',
     'sigi.apps.birt.views.menu'),
    # graficos de perguntas
    (r'^sigi/diagnosticos/graficos/$',
     'sigi.apps.diagnosticos.views.graficos'),
    (r'^sigi/api/diagnosticos/$',
     'sigi.apps.diagnosticos.views.grafico_api'),
    # Views dos serviços SEIT
    (r'^sigi/servicos/listacasas/(?P<sigla>\w+)',
     'sigi.apps.servicos.views.casas_usam_servico'),
    # automatic interface based on admin
    #(r'^sigi/(.*)', sites.default.root),
    (r'^sigi/', include(sites.default.urls)),
)

if settings.DEBUG:
    urlpatterns = patterns(
        '',

        # static files
        (r'^sigi/media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),

        (r'^404/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'admin/404.html'}),

        (r'^500/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'admin/500.html'}),

        (r'^503/$', 'django.views.generic.simple.direct_to_template',
            {'template': '503.html'}),
    ) + urlpatterns
