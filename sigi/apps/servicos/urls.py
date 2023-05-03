from django.urls import path
from sigi.apps.servicos import views

urlpatterns = [
    path(
        "casasatendidas/",
        views.CasasAtendidasListView.as_view(),
        name="servicos_casas_atendidas",
        kwargs={"param": "_all_"},
    ),
    path(
        "casasatendidas/<str:param>/",
        views.CasasAtendidasListView.as_view(),
        name="servicos_casas_atendidas",
    ),
]
