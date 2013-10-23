from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', RedirectView.as_view(url='/sigi/'), name='go-to-sigi'),

    url(r'^sigi/', include(admin.site.urls)),
)
