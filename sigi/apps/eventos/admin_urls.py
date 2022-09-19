from django.urls import path, include
from sigi.apps.eventos import views

urlpatterns = [
    path("calendario/", views.calendario, name="eventos_calendario"),
    path(
        "alocacaoequipe/", views.alocacao_equipe, name="eventos_alocacaoequipe"
    ),
    path(
        "evento/<int:id>/declaracao/",
        views.declaracao,
        name="evento-declaracao",
    ),
]
