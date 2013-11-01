from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/sigi/'), name='go-to-sigi'),

    # url(r'^sigi/servidores/', include('sigi.apps.servidores.urls')),
    url(r'^sigi/parlamentares/parlamentar/', include('sigi.apps.parlamentares.urls')),
    url(r'^sigi/casas/casalegislativa/', include('sigi.apps.casas.urls')),
    url(r'^sigi/convenios/convenio/', include('sigi.apps.convenios.urls')),

    url(r'^sigi/', include(admin.site.urls)),
)
