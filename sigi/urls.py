#-*- coding:utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/sigi/'), name='go-to-sigi'),

    url(r'^sigi/parlamentares/parlamentar/', include('sigi.apps.parlamentares.urls')),
    url(r'^sigi/casas/casalegislativa/', include('sigi.apps.casas.urls')),
    url(r'^sigi/convenios/convenio/', include('sigi.apps.convenios.urls')),
    url(r'^sigi/diagnosticos/', include('sigi.apps.diagnosticos.urls')),
    url(r'^sigi/servidores/', include('sigi.apps.servidores.urls')),
    url(r'^sigi/dashboard/', include('sigi.apps.metas.urls')),
    url(r'^sigi/servicos/', include('sigi.apps.servicos.urls')),

    url(r'^sigi/', include(admin.site.urls)),
)
