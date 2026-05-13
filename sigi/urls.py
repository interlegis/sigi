"""sigi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, RedirectView
from dashboard.registry import dashboard

admin.site.site_header = admin.site.site_title = _("SIGI")
admin.site.index_title = _("Sistema de Informações Gerenciais do Interlegis")

urlpatterns = [
    path("casas/", include("sigi.apps.casas.urls")),
    path("ocorrencias/", include("sigi.apps.ocorrencias.urls")),
    path("parlamentares/", include("sigi.apps.parlamentares.urls")),
    path("servicos/", include("sigi.apps.servicos.urls")),
    path("admin/casas/", include("sigi.apps.casas.admin_urls")),
    path("admin/espacos/", include("sigi.apps.espacos.admin_urls")),
    path("admin/eventos/", include("sigi.apps.eventos.admin_urls")),
    path("admin/convenios/", include("sigi.apps.convenios.urls")),
    path("admin/ocorrencias/", include("sigi.apps.ocorrencias.admin_urls")),
    path("admin/utils/", include("sigi.apps.utils.admin_urls")),
    path("admin/", admin.site.urls),
    path("dash/", dashboard.urls),
    path(
        "api/",
        RedirectView.as_view(pattern_name="swagger-ui", permanent=False),
    ),
    path(
        "api/doc/",
        RedirectView.as_view(pattern_name="swagger-ui", permanent=False),
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="openapi-schema"),
    path(
        "api/doc/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="openapi-schema"),
        name="swagger-ui",
    ),
    path(
        "api/doc/redoc/",
        SpectacularRedocView.as_view(url_name="openapi-schema"),
        name="redoc",
    ),
    path("api/casas/", include("sigi.apps.casas.api_urls")),
    path("api/eventos/", include("sigi.apps.eventos.api_urls")),
    path("api/servicos/", include("sigi.apps.servicos.api_urls")),
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
