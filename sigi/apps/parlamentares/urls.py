from django.urls import path, include
from sigi.apps.parlamentares import views

app_name = "parlamentares"

urlpatterns = [
    path(
        "parlamentar/",
        views.ParlamentarListView.as_view(),
        name="parlamentar_listview",
    ),
    path(
        "parlamentar/<int:pk>/",
        views.ParlamentarUpdateView.as_view(),
        name="parlamentar_update",
    ),
    path(
        "parlamentar/<int:casa_id>/json/",
        views.parlamentares_casa,
        name="parlamentar_json",
    ),
    path("parlamentar/data/", views.parlamentar_data, name="parlamentar_data"),
]
