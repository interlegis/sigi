# coding: utf-8
from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import MapaView
from sigi.apps.servicos import views


urlpatterns = [
    url(r'^manifesta/$', views.casa_manifesta_view, name="casa-manifesta-view"),
    url(r'^munatenjson/(?P<servico>\w+)/$', views.municipios_atendidos, name="municipios-atendidos"),
    url(r'^mapa/(?P<servico>\w+)/$', MapaView.as_view(), name="servicos-mapa"),
    # url(r'^listacasas/(?P<sigla>\w+)', views.casas_usam_servico, name="casas-usam-servico"),
]
