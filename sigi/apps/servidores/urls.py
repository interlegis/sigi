# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'sigi.apps.servidores.views',

    # Reports servidores
    url(r'^servidores_por_funcao.pdf$', 'servidores_por_funcao', name='servidores-funcao-pdf'),
    url(r'^servidores_por_cargo.pdf$', 'servidores_por_cargo', name='servidores-cargo-pdf'),
)
