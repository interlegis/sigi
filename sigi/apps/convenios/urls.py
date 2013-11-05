# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('sigi.apps.convenios.views',
	url(r'^reports/$', 'report', name='convenios-report'),
	url(r'^carrinho/$', 'visualizar_carrinho', name='visualizar-carrinho'),
	url(r'^carrinho/excluir_carrinho/$', 'excluir_carrinho', name='excluir-carrinho'),
	url(r'^carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho', name='deleta-itens-carrinho'),
	# url(r'^$', '', name=''),
)