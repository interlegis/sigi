from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import databrowse
from django.db.models import get_models

admin.autodiscover()
map(databrowse.site.register, get_models())

urlpatterns = patterns(
    '',

    (r'^doc/', include('django.contrib.admindocs.urls')),
    (r'^(.*)', admin.site.root),

    # databrowse
    (r'^databrowse/(.*)', databrowse.site.root),

    # bug report
    #(r'^bug_report/$', 'sigi.views.bug_report'),
)

if settings.MAINTENANCE:
    urlpatterns = patterns('',
        (r'.*', 'sigi.views.service_unavailable')
    ) + urlpatterns

if settings.DEBUG:
    urlpatterns += patterns(
        '',

        # static files
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),

        (r'^404/$', 'django.views.generic.simple.direct_to_template',
            {'template': '404.html'}),

        (r'^500/$', 'django.views.generic.simple.direct_to_template',
            {'template': '500.html'}),

        (r'^503/$', 'django.views.generic.simple.direct_to_template',
            {'template': '503.html'}),
    )
