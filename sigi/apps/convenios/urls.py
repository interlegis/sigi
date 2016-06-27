# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'sigi.apps.convenios.views',

    url(r'^convenio/reports/$', 'report', name='convenios-report'),
    url(r'^convenio/carrinho/$', 'visualizar_carrinho', name='visualizar-carrinho'),
    url(r'^convenio/carrinho/excluir_carrinho/$', 'excluir_carrinho', name='excluir-carrinho'),  # tagerror
    url(r'^convenio/carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho', name='deleta-itens-carrinho'),  # tagerror
    url(r'^convenio/csv/$', 'export_csv', name='convenios-csv'),
    url(r'^reportsRegiao/(?P<regiao>\w+)/$', 'report_regiao', name='convenios-report_regiao_pdf'),
)
