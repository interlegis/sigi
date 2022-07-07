from django.urls import path
from sigi.apps.ocorrencias import views

urlpatterns = [
    path("painel/", views.painel_ocorrencias, name="painel-ocorrencias"),
    path("convenio/painel/", views.painel_convenio, name="painel-convenio"),
    path(
        "convenio/painel/<int:ocorrencia_id>/",
        views.painel_convenio,
        name="painel-convenio",
    ),
]
