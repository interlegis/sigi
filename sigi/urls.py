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
    (r'^casas/casalegislativa/reports/',
    'sigi.apps.casas.views.report'),
    (r'^casas/casalegislativa/csv/',
    'sigi.apps.casas.views.export_csv'),
    (r'^casas/casalegislativa/casas_sem_convenio_report/',
    'sigi.apps.casas.views.casas_sem_convenio_report'),
    (r'^convenios/convenio/reports_por_cm/',
     'sigi.apps.convenios.views.report_por_cm'),
    (r'^convenios/convenio/reports_por_al/',
     'sigi.apps.convenios.views.report_por_al'),
    (r'^convenios/convenio/reportsRegiao/',
     'sigi.apps.convenios.views.reportRegiao'),
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
