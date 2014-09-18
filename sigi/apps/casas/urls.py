# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('sigi.apps.casas.views',

    # Informacoes de uma casa legislativa
    url(r'^report_complete/$', 'report_complete', name='report-complete-all'),
    url(r'^(?P<id>\w+)/report_complete/$', 'report_complete', name='report-complete-id'),

    # Reports Labels
    url(r'^labels/$', 'labels_report', name='labels-report-all'),
    url(r'^(?P<id>\w+)/labels/$', 'labels_report', name='labels-report-id'),

    # Reports Labels Parlamentar
    url(r'^labels_parlamentar/$', 'labels_report_parlamentar', name='lebels-report-parlamentar-all'),
    url(r'^(?P<id>\w+)/labels_parlamentar/$', 'labels_report_parlamentar', name='labels-report-parlamentar-id'),


    # Reports labels sem presidente
    url(r'^labels_sem_presidente/$', 'labels_report_sem_presidente', name='labels-report-sem-presidente-all'),
    url(r'^(?P<id>\w+)/labels_sem_presidente/$', 'labels_report_sem_presidente', name='labels-report-sem-presidente-id'),

    # Reports casas sem convenio
    url(r'^reports/$', 'report', name='casa-report'),
    url(r'^casas_sem_convenio_report/$', 'casas_sem_convenio_report', name='casas-sem-convenio-report'),

    # CSV
    url(r'^csv/$', 'export_csv', name='casa-export-csv'),  # Error

    # Carrinho
    url(r'^carrinho/$', 'visualizar_carrinho', name='visualizar-carrinho'),
    url(r'^carrinho/excluir_carrinho/$', 'excluir_carrinho', name='excluir-carrinho'),  # Error
    url(r'^carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho', name='deleta-itens-carrinho'),  # Error

)
