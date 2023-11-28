from django.urls import path, include
from sigi.apps.espacos import views

urlpatterns = [
    path("agenda/", views.Agenda.as_view(), name="espacos_agenda"),
    path("usoespacos/", views.UsoEspacos.as_view(), name="espacos_usoespaco"),
]
