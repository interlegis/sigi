from django.urls import path, re_path
from sigi.apps.ocorrencias import views

app_name = "ocorrencias"

urlpatterns = [
    path(
        "ocorrencia/",
        views.OcorrenciaListView.as_view(),
        name="ocorrencia_listview",
    ),
    path(
        "ocorrencia/oficina/casa/",
        views.OficinaSelecionaCasaView.as_view(),
        name="ocorrencia_oficina_seleciona_casa",
    ),
    path(
        "ocorrencia/oficina/create/",
        views.SolicitaOficinaCreateView.as_view(),
        name="solicita_oficina_create",
    ),
    path(
        "ocorrencia/<int:pk>/oficina/",
        views.SolicitaOficinaView.as_view(),
        name="solicita_oficina_view",
    ),
    path(
        "ocorrencia/convenio/casa/",
        views.ConvenioSelecionaCasaView.as_view(),
        name="ocorrencia_convenio_seleciona_casa",
    ),
    path(
        "ocorrencia/convenio/create/",
        views.SolicitaConvenioCreateView.as_view(),
        name="solicita_convenio",
    ),
    path(
        "ocorrencia/<int:pk>/convenio/",
        views.SolicitaConvenioCreateView.as_view(),
        name="solicita_convenio",
    ),
    re_path(
        "ocorrencia/(?P<pk>\d+)/convenio/(?P<tab>casa|presidente|contato|documentos|resumo)/",
        views.SolicitaConvenioCreateView.as_view(),
        name="solicita_convenio",
    ),
]
