from django.urls import path
from sigi.apps.ocorrencias import views

urlpatterns = [
    path(
        "painel/",
        views.PainelOcorrenciaView.as_view(),
        name="ocorrencias_painel",
    ),
    path(
        "painel/oficina/<int:pk>/",
        views.OficinaChangeView.as_view(),
        name="ocorrencias_painel_oficina",
    ),
    path(
        "painel/convenio/<int:pk>/",
        views.ConvenioChangeView.as_view(),
        name="ocorrencias_painel_convenio",
    ),
]
