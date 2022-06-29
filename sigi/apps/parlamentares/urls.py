from django.urls import path, include
from sigi.apps.parlamentares import views

urlpatterns = [
    path(
        "parlamentar_json/<int:casa_id>/",
        views.parlamentar_json,
        name="parlamentar-json",
    ),
]
