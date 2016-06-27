# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'sigi.apps.ocorrencias.views',
    # Painel de ocorrencias
    url(r'^painel/$', 'painel_ocorrencias', name='painel-ocorrencias'),
    url(r'^painel/buscanominal/$', 'busca_nominal', {"origin": "tudo"}, name='painel-buscanominal'),
    url(r'^painel/buscanominal/casa/$', 'busca_nominal', {"origin": "casa"}, name='painel-buscacasa'),
    url(r'^painel/buscanominal/servidor/$', 'busca_nominal', {"origin": "servidor"}, name='painel-buscaservidor'),
    url(r'^painel/buscanominal/servico/$', 'busca_nominal', {"origin": "servico"}, name='painel-buscaservico'),
    url(r'^mudaprioridade/$', 'muda_prioridade', name='ocorrencia-mudaprioridade'),
    url(r'^excluianexo/$', 'exclui_anexo', name='ocorrencia-excluianexo'),
    url(r'^incluianexo/$', 'inclui_anexo', name='ocorrencia-incluianexo'),
    url(r'^anexosnippet/$', 'anexo_snippet', name='ocorrencia-anexosnippet'),
    url(r'^incluicomentario/$', 'inclui_comentario', name='ocorrencia-incluicomentario'),
    url(r'^incluiocorrencia/$', 'inclui_ocorrencia', name='ocorrencia-incluiocorrencia'),
)
