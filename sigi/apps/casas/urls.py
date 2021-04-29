# coding: utf-8
from django.conf.urls import patterns, url
from sigi.apps.casas.views import importa_casas


urlpatterns = patterns(
    'sigi.apps.casas.views',

    # Informacoes de uma casa legislativa
    url(r'^orgao/report_complete/$', 'report_complete', name='report-complete-all'),
    url(r'^orgao/(?P<id>\w+)/report_complete/$', 'report_complete', name='report-complete-id'),

    # Reports Labels
    url(r'^orgao/labels/$', 'labels_report', name='labels-report-all'),
    url(r'^orgao/(?P<id>\w+)/labels/$', 'labels_report', name='labels-report-id'),

    # Reports Labels Parlamentar
    url(r'^orgao/labels_parlamentar/$', 'labels_report_parlamentar', name='lebels-report-parlamentar-all'),
    url(r'^orgao/(?P<id>\w+)/labels_parlamentar/$', 'labels_report_parlamentar', name='labels-report-parlamentar-id'),


    # Reports labels sem presidente
    url(r'^orgao/labels_sem_presidente/$', 'labels_report_sem_presidente', name='labels-report-sem-presidente-all'),
    url(r'^orgao/(?P<id>\w+)/labels_sem_presidente/$', 'labels_report_sem_presidente', name='labels-report-sem-presidente-id'),

    # Reports casas sem convenio
    url(r'^orgao/reports/$', 'report', name='casa-report'),
    url(r'^orgao/casas_sem_convenio_report/$', 'casas_sem_convenio_report', name='casas-sem-convenio-report'),

    # CSV
    url(r'^orgao/csv/$', 'export_csv', name='casa-export-csv'),  # Error

    # Carrinho
    url(r'^orgao/carrinho/$', 'visualizar_carrinho', name='visualizar-carrinho'),
    url(r'^orgao/carrinho/excluir_carrinho/$', 'excluir_carrinho', name='excluir-carrinho'),  # Error
    url(r'^orgao/carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho', name='deleta-itens-carrinho'),  # Error
    url(r'^portfolio/$', 'portfolio', name='casas-portfolio'),
    url(r'^carteira/$', 'painel_relacionamento', name='casas-carteira'),

    # Atualização por CSV
    url(r'^orgao/importa/$', importa_casas.as_view(), name='importar-casas'),
)
