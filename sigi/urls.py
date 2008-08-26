from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import databrowse
from django.db.models import get_models
from sigi import sites

map(databrowse.site.register, get_models())

urlpatterns = patterns(
    '',

    # databrowse
    (r'^databrowse/(.*)', databrowse.site.root),

    # bug report
    #(r'^bug_report/$', 'sigi.views.bug_report'),

    # admin docs
    (r'^doc/', include('django.contrib.admindocs.urls')),

    # automatic interface based on admin
    (r'^(.*)', sites.default.root),
)

if settings.DEBUG:
    urlpatterns = patterns(
        '',

        # static files
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),

        (r'^404/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'admin/404.html'}),

        (r'^500/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'admin/500.html'}),

        (r'^503/$', 'django.views.generic.simple.direct_to_template',
            {'template': '503.html'}),
    ) + urlpatterns
