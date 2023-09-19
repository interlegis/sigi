"""sigi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework.schemas import get_schema_view
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("casas/", include("sigi.apps.casas.urls")),
    path("ocorrencias/", include("sigi.apps.ocorrencias.urls")),
    path("parlamentares/", include("sigi.apps.parlamentares.urls")),
    path("servicos/", include("sigi.apps.servicos.urls")),
    path("admin/casas/", include("sigi.apps.casas.admin_urls")),
    path("admin/eventos/", include("sigi.apps.eventos.admin_urls")),
    path("admin/convenios/", include("sigi.apps.convenios.urls")),
    path("admin/ocorrencias/", include("sigi.apps.ocorrencias.admin_urls")),
    path("admin/", admin.site.urls),
    path(
        "api/doc/schema.yaml",
        get_schema_view(
            title="SIGI Open API Schema",
            description="API for SIGI opendata",
            version="1.0.0",
        ),
        name="openapi-schema",
    ),
    path(
        "api/doc/swagger-ui/",
        TemplateView.as_view(
            template_name="sigi/api/swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
    path(
        "api/doc/redoc/",
        TemplateView.as_view(
            template_name="sigi/api/redoc.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="redoc",
    ),
    path("api/eventos/", include("sigi.apps.eventos.api_urls")),
    path("tinymce/", include("tinymce.urls")),
    path("accounts/", include("sigi.apps.home.accounts_urls")),
    path("", include("sigi.apps.home.urls")),
]

if settings.DEBUG:
    urlpatterns = (
        urlpatterns
        + [path("__debug__/", include("debug_toolbar.urls"))]
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
