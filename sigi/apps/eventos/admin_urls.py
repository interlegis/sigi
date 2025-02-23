from django.urls import path
from sigi.apps.eventos import views
from sigi.apps.eventos.views import EventosPorUfReportView

urlpatterns = [
    path("calendario/", views.calendario, name="eventos_calendario"),
    path(
        "alocacaoequipe/", views.alocacao_equipe, name="eventos_alocacaoequipe"
    ),
    path("eventosporuf/", EventosPorUfReportView.as_view(), name="eventos_eventosporuf"),
    path(
        "alunosporuf/",
        views.AlunosPorUfReportView.as_view(),
        name="eventos_alunosporuf",
    ),
    path(
        "solicitacoesporperiodo/",
        views.solicitacoes_por_periodo,
        name="eventos_solicitacoesporperiodo",
    ),
    path(
        "custoseventos/",
        views.CustosEventosReport.as_view(),
        name="eventos_custoseventos",
    ),
    path(
        "custosservidor/",
        views.CustosServidorReport.as_view(),
        name="eventos_custosservidor",
    ),
]
