# coding: utf-8
from django.conf.urls import url
from sigi.apps.parlamentares import views

urlpatterns = [
    # Reports labels parlamentares
    url(r'^parlamentar/labels/$', views.labels_report, name='labels-report-all'),
    url(r'^parlamentar/(?P<id>\w+)/labels/$', views.labels_report, name='labels-report-id'),

    # Carrinho
    url(r'^parlamentar/carrinho/$', views.visualizar_carrinho, name='visualizar-carrinho'),
    url(r'^parlamentar/carrinho/deleta_itens_carrinho$', views.deleta_itens_carrinho, name='deleta-itens-carrinho'),

    # A view excluir_carrinho n existe ainda.
    # url(r'^parlamentar/carrinho/exluir_carrinho$', views.excluir_carrinho, name='excluir-carrinho'),
]
