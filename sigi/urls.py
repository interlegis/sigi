#-*- coding:utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.site.index_template = 'index.html'
admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^parlamentares/parlamentar/', include('sigi.apps.parlamentares.urls')),
    url(r'^casas/casalegislativa/', include('sigi.apps.casas.urls')),
    url(r'^convenios/convenio/', include('sigi.apps.convenios.urls')),
    url(r'^diagnosticos/', include('sigi.apps.diagnosticos.urls')),
    url(r'^servidores/', include('sigi.apps.servidores.urls')),
    url(r'^servicos/', include('sigi.apps.servicos.urls')),
    url(r'^saberes/', include('sigi.apps.saberes.urls')),
    url(r'^dashboard/', include('sigi.apps.metas.urls')),

    url(r'^', include(admin.site.urls)),

    # to enable language selection
    # Suspended
    #url(r'^i18n/', include('django.conf.urls.i18n')),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns = patterns(
        '',

        url(r'^404/$', TemplateView.as_view(template_name='404.html')),
        url(r'^500/$', TemplateView.as_view(template_name='500.html')),
        url(r'^503/$', TemplateView.as_view(template_name='503.html')),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT, }),
    ) + urlpatterns
