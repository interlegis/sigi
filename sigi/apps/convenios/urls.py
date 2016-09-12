# coding: utf-8
from django.conf.urls import url
from sigi.apps.convenios import views

urlpatterns = [
    url(r'^convenio/reports/$', views.report, name='convenios-report'),
    url(r'^convenio/carrinho/$', views.visualizar_carrinho, name='visualizar-carrinho'),
    url(r'^convenio/carrinho/excluir_carrinho/$', views.excluir_carrinho, name='excluir-carrinho'),  # tagerror
    url(r'^convenio/carrinho/deleta_itens_carrinho$', views.deleta_itens_carrinho, name='deleta-itens-carrinho'),  # tagerror
    url(r'^convenio/csv/$', views.export_csv, name='convenios-csv'),
    url(r'^reportsRegiao/(?P<regiao>\w+)/$', views.report_regiao, name='convenios-report_regiao_pdf'),
]
