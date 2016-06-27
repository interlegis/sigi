# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'sigi.apps.casas.views',

    # Informacoes de uma casa legislativa
    url(r'^casalegislativa/report_complete/$', 'report_complete', name='report-complete-all'),
    url(r'^casalegislativa/(?P<id>\w+)/report_complete/$', 'report_complete', name='report-complete-id'),

    # Reports Labels
    url(r'^casalegislativa/labels/$', 'labels_report', name='labels-report-all'),
    url(r'^casalegislativa/(?P<id>\w+)/labels/$', 'labels_report', name='labels-report-id'),

    # Reports Labels Parlamentar
    url(r'^casalegislativa/labels_parlamentar/$', 'labels_report_parlamentar', name='lebels-report-parlamentar-all'),
    url(r'^casalegislativa/(?P<id>\w+)/labels_parlamentar/$', 'labels_report_parlamentar', name='labels-report-parlamentar-id'),


    # Reports labels sem presidente
    url(r'^casalegislativa/labels_sem_presidente/$', 'labels_report_sem_presidente', name='labels-report-sem-presidente-all'),
    url(r'^casalegislativa/(?P<id>\w+)/labels_sem_presidente/$', 'labels_report_sem_presidente', name='labels-report-sem-presidente-id'),

    # Reports casas sem convenio
    url(r'^casalegislativa/reports/$', 'report', name='casa-report'),
    url(r'^casalegislativa/casas_sem_convenio_report/$', 'casas_sem_convenio_report', name='casas-sem-convenio-report'),

    # CSV
    url(r'^casalegislativa/csv/$', 'export_csv', name='casa-export-csv'),  # Error

    # Carrinho
    url(r'^casalegislativa/carrinho/$', 'visualizar_carrinho', name='visualizar-carrinho'),
    url(r'^casalegislativa/carrinho/excluir_carrinho/$', 'excluir_carrinho', name='excluir-carrinho'),  # Error
    url(r'^casalegislativa/carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho', name='deleta-itens-carrinho'),  # Error
    url(r'^portfolio/$', 'portfolio', name='casas-portfolio'),
    url(r'^carteira/$', 'painel_relacionamento', name='casas-carteira'),
)
