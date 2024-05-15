from django.urls import path
from sigi.apps.convenios import views

urlpatterns = [
    path(
        "errosgescon/",
        views.report_erros_gescon,
        name="convenios-report_erros_gescon",
    ),
    path(
        "reportsRegiao/<str:regiao>/",
        views.report_regiao,
        name="convenios-report_regiao_pdf",
    ),
    path("importar/", views.importar_gescon, name="importar-gescon"),
]
