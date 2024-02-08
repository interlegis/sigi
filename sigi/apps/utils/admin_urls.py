from django.urls import path, include
from sigi.apps.utils import views

urlpatterns = [
    path(
        "runjob/<str:job_name>/",
        views.user_run_job,
        name="utils_runjob",
    ),
]
