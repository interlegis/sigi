# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns(
    'sigi.apps.eventos.views',
    # Painel de ocorrencias
    url(r'^calendario/$', 'calendario', name='eventos-calendario'),
    url(r'^alocacaoequipe/$', 'alocacao_equipe', name='eventos-alocacaoequipe'),
    # Carrinho
    url(r'^evento/carrinho/$', 'visualizar_carrinho',
        name='visualizar-carrinho-evento'),
    url(r'^evento/carrinho/excluir_carrinho/$', 'excluir_carrinho',
        name='excluir-carrinho-evento'),  # Error
    url(r'^evento/carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho',
        name='deleta-itens-carrinho-evento'),  # Error
    url(r'^evento/csv/$', 'export_csv', name='evento-export-csv'),  # Error

)
