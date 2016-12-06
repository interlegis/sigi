# coding: utf-8
from django.conf.urls import url
from sigi.apps.casas import views

urlpatterns = [

    # Informacoes de uma casa legislativa
    url(r'^casalegislativa/report_complete/$', views.report_complete, name='report-complete-all'),
    url(r'^casalegislativa/(?P<id>\w+)/report_complete/$', views.report_complete, name='report-complete-id'),

    # Reports Labels
    url(r'^casalegislativa/labels/$', views.labels_report, name='labels-report-all'),
    url(r'^casalegislativa/(?P<id>\w+)/labels/$', views.labels_report, name='labels-report-id'),

    # Reports Labels Parlamentar
    url(r'^casalegislativa/labels_parlamentar/$', views.labels_report_parlamentar, name='lebels-report-parlamentar-all'),
    url(r'^casalegislativa/(?P<id>\w+)/labels_parlamentar/$', views.labels_report_parlamentar, name='labels-report-parlamentar-id'),


    # Reports labels sem presidente
    url(r'^casalegislativa/labels_sem_presidente/$', views.labels_report_sem_presidente, name='labels-report-sem-presidente-all'),
    url(r'^casalegislativa/(?P<id>\w+)/labels_sem_presidente/$', views.labels_report_sem_presidente, name='labels-report-sem-presidente-id'),

    # Reports casas sem convenio
    url(r'^casalegislativa/reports/$', views.report, name='casa-report'),
    url(r'^casalegislativa/casas_sem_convenio_report/$', views.casas_sem_convenio_report, name='casas-sem-convenio-report'),

    # CSV
    url(r'^casalegislativa/csv/$', views.export_csv, name='casa-export-csv'),  # Error

    # Carrinho
    url(r'^casalegislativa/carrinho/$', views.visualizar_carrinho, name='visualizar-carrinho'),
    url(r'^casalegislativa/carrinho/excluir_carrinho/$', views.excluir_carrinho, name='excluir-carrinho'),  # Error
    url(r'^casalegislativa/carrinho/deleta_itens_carrinho$', views.deleta_itens_carrinho, name='deleta-itens-carrinho'),  # Error
    url(r'^portfolio/$', views.portfolio, name='casas-portfolio'),
    url(r'^carteira/$', views.painel_relacionamento, name='casas-carteira'),
]
