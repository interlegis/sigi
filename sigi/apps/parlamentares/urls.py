# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'sigi.apps.parlamentares.views',

    # Reports labels parlamentares
    url(r'^parlamentar/labels/$', 'labels_report', name='labels-report-all'),
    url(r'^parlamentar/(?P<id>\w+)/labels/$', 'labels_report', name='labels-report-id'),

    # Carrinho
    url(r'^parlamentar/carrinho/$', 'visualizar_carrinho', name='visualizar-carrinho'),
    url(r'^parlamentar/carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho', name='deleta-itens-carrinho'),

    # A view excluir_carrinho n existe ainda.
    # url(r'^parlamentar/carrinho/exluir_carrinho$', 'excluir_carrinho', name='excluir-carrinho'),
)
