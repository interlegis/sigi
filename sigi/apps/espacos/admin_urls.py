from django.urls import path, include
from sigi.apps.espacos import views

urlpatterns = [
    path("agenda/", views.Agenda.as_view(), name="espacos_agenda"),
]
