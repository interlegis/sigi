from django.urls import path
from sigi.apps.eventos import views
from sigi.apps.eventos.views import EventosPorUfReportView, SolicitacoesPorPeriodoReportView, CalendarioReportView, AlocacaoEquipeReportView

urlpatterns = [
    path("calendario/", CalendarioReportView.as_view(), name="eventos_calendario"),
    path(
        "alocacaoequipe/", AlocacaoEquipeReportView.as_view(), name="eventos_alocacaoequipe"
    ),
    path("eventosporuf/", EventosPorUfReportView.as_view(), name="eventos_eventosporuf"),
    path(
        "alunosporuf/",
        views.AlunosPorUfReportView.as_view(),
        name="eventos_alunosporuf",
    ),
    path(
        "solicitacoesporperiodo/",
        SolicitacoesPorPeriodoReportView.as_view(),
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
