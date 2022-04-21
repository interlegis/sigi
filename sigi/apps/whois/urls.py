# coding: utf-8
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from . import views

urlpatterns = patterns(
    "",
    url(r"^(?P<dominio>.+)$", views.whois_query),
)
