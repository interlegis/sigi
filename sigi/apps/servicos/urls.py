# coding: utf-8
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from .views import MapaView


urlpatterns = patterns(
    "sigi.apps.servicos.views",
    url(r"^manifesta/$", "casa_manifesta_view", name="casa-manifesta-view"),
    url(
        r"^servico/carrinho/$",
        "visualizar_carrinho",
        name="visualizar-carrinho",
    ),
    url(
        r"^servico/carrinho/excluir_carrinho/$",
        "excluir_carrinho",
        name="excluir-carrinho",
    ),  # tagerror
    url(
        r"^servico/carrinho/deleta_itens_carrinho$",
        "deleta_itens_carrinho",
        name="deleta-itens-carrinho",
    ),  # tagerror
    url(r"^servico/csv/$", "export_csv", name="servicos-csv"),
    url(
        r"^munatenjson/(?P<servico>\w+)/$",
        "municipios_atendidos",
        name="municipios-atendidos",
    ),
    url(r"^mapa/(?P<servico>\w+)/$", MapaView.as_view(), name="servicos-mapa"),
    # url(r'^listacasas/(?P<sigla>\w+)', 'casas_usam_servico', name="casas-usam-servico"),
)
