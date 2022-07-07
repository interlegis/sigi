from django.urls import path, include
from sigi.apps.parlamentares import views

urlpatterns = [
    path(
        "parlamentarjson/<int:casa_id>/",
        views.parlamentares_casa,
        name="parlamentar-json",
    ),
    path("parlamentardata/", views.parlamentar_data, name="parlamentar-data"),
]
