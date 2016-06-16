# coding: utf-8
from django.conf.urls import url
from sigi.apps.ocorrencias import views

urlpatterns = [
    # Painel de ocorrencias
    url(r'^painel/$', views.painel_ocorrencias, name='painel-ocorrencias'),
    url(r'^painel/buscanominal/$', views.busca_nominal, {"origin": "tudo"}, name='painel-buscanominal'),
    url(r'^painel/buscanominal/casa/$', views.busca_nominal, {"origin": "casa"}, name='painel-buscacasa'),
    url(r'^painel/buscanominal/servidor/$', views.busca_nominal, {"origin": "servidor"}, name='painel-buscaservidor'),
    url(r'^painel/buscanominal/servico/$', views.busca_nominal, {"origin": "servico"}, name='painel-buscaservico'),
    url(r'^mudaprioridade/$', views.muda_prioridade, name='ocorrencia-mudaprioridade'),
    url(r'^excluianexo/$', views.exclui_anexo, name='ocorrencia-excluianexo'),
    url(r'^incluianexo/$', views.inclui_anexo, name='ocorrencia-incluianexo'),
    url(r'^anexosnippet/$', views.anexo_snippet, name='ocorrencia-anexosnippet'),
    url(r'^incluicomentario/$', views.inclui_comentario, name='ocorrencia-incluicomentario'),
    url(r'^incluiocorrencia/$', views.inclui_ocorrencia, name='ocorrencia-incluiocorrencia'),
]
