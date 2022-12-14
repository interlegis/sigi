from django.urls import path
from sigi.apps.servicos import views

urlpatterns = [
    path(
        "casasatendidas/",
        views.CasasAtendidasListView.as_view(),
        name="servicos_casas_atendidas",
        kwargs={"sigla_uf": "_all_"},
    ),
    path(
        "casasatendidas/<str:sigla_uf>/",
        views.CasasAtendidasListView.as_view(),
        name="servicos_casas_atendidas",
    ),
]
