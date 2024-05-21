from django.urls import path
from sigi.apps.casas import views

urlpatterns = [
    path("carteira/", views.painel_relacionamento, name="casas_carteira"),
    path("gerentes/", views.GerentesListView.as_view(), name="casas_gerentes"),
    path(
        "cnpjduplicado/",
        views.CnpjDuplicadoReport.as_view(),
        name="casas_cnpj_duplicado",
    ),
    path(
        "cnpjerrado/",
        views.CnpjErradoReport.as_view(),
        name="casas_cnpj_errado",
    ),
]
