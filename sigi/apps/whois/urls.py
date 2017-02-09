# coding: utf-8
from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    url(r'^(?P<dominio>.+)$', views.whois_query),
]

