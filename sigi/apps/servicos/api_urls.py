from django.urls import path
from sigi.apps.servicos import views

urlpatterns = [
    path("resumoprodutos/", views.ResumoProdutosApiView.as_view()),
    path("", views.ServicoListView.as_view()),
]
