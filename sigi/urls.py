#-*- coding:utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
import sites

# register admin filters
import admin.filterspecs

urlpatterns = patterns(
    '',

    # Diagnosticos
    url(r'sigi/mobile/diagnosticos/', include('sigi.apps.diagnosticos.urls')),

    # Informacoes de uma casa legislativa
    (r'^casas/casalegislativa/(?P<id>\w+)/report_complete/',
     'sigi.apps.casas.views.report_complete'),
     (r'^casas/casalegislativa/report_complete/',
     'sigi.apps.casas.views.report_complete'),
    # reports labels
    (r'^casas/casalegislativa/labels/',
     'sigi.apps.casas.views.labels_report'),
    (r'^casas/casalegislativa/(?P<id>\w+)/labels/',
     'sigi.apps.casas.views.labels_report'),
     # reports labels sem presidente
    (r'^casas/casalegislativa/labels_sem_presidente/',
     'sigi.apps.casas.views.labels_report_sem_presidente'),
    (r'^casas/casalegislativa/(?P<id>\w+)/labels_sem_presidente/',
     'sigi.apps.casas.views.labels_report_sem_presidente'),
    # reports casa    
    (r'^casas/casalegislativa/reports/',
    'sigi.apps.casas.views.report'),    
    (r'^casas/casalegislativa/casas_sem_convenio_report/',
    'sigi.apps.casas.views.casas_sem_convenio_report'),
    # reports convenios
    (r'^convenios/convenio/reports/',
     'sigi.apps.convenios.views.report'),         
     #Carrinho Casa
     (r'^casas/casalegislativa/carrinho/deleta_itens_carrinho',
     'sigi.apps.casas.views.deleta_itens_carrinho'),
     (r'^casas/casalegislativa/carrinho/excluir_carrinho',
     'sigi.apps.casas.views.excluir_carrinho'),
     (r'^casas/casalegislativa/carrinho/',
     'sigi.apps.casas.views.visualizar_carrinho'),
     #Carrinho Convenio
     (r'^convenios/convenio/carrinho/deleta_itens_carrinho',
     'sigi.apps.convenios.views.deleta_itens_carrinho'),
      (r'^convenios/convenio/carrinho/excluir_carrinho',
     'sigi.apps.convenios.views.excluir_carrinho'),
     (r'^convenios/convenio/carrinho/',
     'sigi.apps.convenios.views.visualizar_carrinho'),
     #CSV Casa
     (r'^casas/casalegislativa/csv/',
    'sigi.apps.casas.views.export_csv'),
    #CSV Convenio
     (r'^convenios/convenio/csv/',
    'sigi.apps.convenios.views.export_csv'),
     # Resumo por região PDF     
     (r'^reportsRegiao/(?P<regiao>\w+)',
     'sigi.apps.convenios.views.report_regiao'),
     # Submenu com Birt reports
     (r'^birt/menu/(?P<folder>\w+)',
     'sigi.apps.birt.views.menu'),
     # Execução com Birt reports
     (r'^birt/run/(?P<file>.+)',
     'sigi.apps.birt.views.run'),
     # Mostrar um relatório em formato HTML
     (r'^birt/showreport/',
     'sigi.apps.birt.views.show'),
     # Menu com Birt reports
     (r'^birt/',
     'sigi.apps.birt.views.menu'),
     
    # automatic interface based on admin
    (r'^(.*)', sites.default.root),
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
