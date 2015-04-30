# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'sigi.apps.parlamentares.views',

    # Reports labels parlamentares
    url(r'^labels/$', 'labels_report', name='labels-report-all'),
    url(r'^(?P<id>\w+)/labels/$', 'labels_report', name='labels-report-id'),

    # Carrinho
    url(r'^carrinho/$', 'visualizar_carrinho', name='visualizar-carrinho'),
    url(r'^carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho', name='deleta-itens-carrinho'),

    # A view excluir_carrinho n existe ainda.
    # url(r'^carrinho/exluir_carrinho$', 'excluir_carrinho', name='excluir-carrinho'),
)
