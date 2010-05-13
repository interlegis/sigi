from django.conf import settings
from django.conf.urls.defaults import *
from sigi import sites

# register admin filters
import sigi.admin.filterspecs

urlpatterns = patterns(
    '',

    # reports labels
    (r'^casas/casalegislativa/labels/',
     'sigi.apps.casas.views.labels_report'),
    (r'^casas/casalegislativa/(?P<id>\w+)/labels/',
     'sigi.apps.casas.views.labels_report'),
    # reports
    (r'^convenios/convenio/reports/',
     'sigi.apps.convenios.views.report'),

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
