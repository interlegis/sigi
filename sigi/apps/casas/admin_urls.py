from django.urls import path, include
from sigi.apps.casas import views

urlpatterns = [
    path("carteira/", views.painel_relacionamento, name="casas_carteira"),
    path("gerentes/", views.GerentesListView.as_view(), name="casas_gerentes"),
]
