# -*- coding: utf-8 -*-
from django.conf.urls import url
from sigi.apps.servidores import views

urlpatterns = [
    # Reports servidores
    url(r'^servidores_por_funcao.pdf$', views.servidores_por_funcao, name='servidores-funcao-pdf'),
    url(r'^servidores_por_cargo.pdf$', views.servidores_por_cargo, name='servidores-cargo-pdf'),
]
