from django.urls import path, include
from sigi.apps.eventos import views

urlpatterns = [
    path(
        "evento/<int:pk>/",
        views.ApiEventoRetrieve.as_view(),
        name="api_eventos_evento_view",
    ),
    path(
        "evento/",
        views.ApiEventoList.as_view(),
        name="api_eventos_evento_list",
    ),
]
