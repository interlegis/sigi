from django.urls import path
from sigi.apps.casas import views

urlpatterns = [
    path("orgaoatendido/", views.ApiOrgaoAtendidoList.as_view()),
    path("orgaoatendido/<int:pk>/", views.ApiOrgaoAtendidoList.as_view()),
    path("orgaoatendido/<slug:uf>/", views.ApiOrgaoAtendidoList.as_view()),
]
