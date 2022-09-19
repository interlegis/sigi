from django.urls import path, include
from sigi.apps.casas import views

app_name = "casas"

urlpatterns = [
    path("orgao/update/", views.CasaUpdateView.as_view(), name="orgao_update"),
    path(
        "funcionario/",
        views.FuncionarioListView.as_view(),
        name="funcionario_listview",
    ),
    path(
        "funcionario/create/",
        views.FuncionarioCreateView.as_view(),
        name="funcionario_create",
    ),
    path(
        "funcionario/<int:pk>/",
        views.FuncionarioUpdateView.as_view(),
        name="funcionario_update",
    ),
    path(
        "funcionario/<int:pk>/delete/",
        views.FuncionarioDeleteView.as_view(),
        name="funcionario_delete",
    ),
]
