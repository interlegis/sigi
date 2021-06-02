# coding: utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    'sigi.apps.metas.views',

    url(r'^$', 'dashboard', name='metas-dashboardsss'),  # tagerror
    url(r'^openmap/$', 'openmap', name='openmap'),
    url(r'^openmapdata/$', 'openmapdata', name='openmapdata'),
    url(r'^openmapdetail/(?P<orgao_id>\w+)/$', 'openmapdetail', name='openmapdetail'),
    url(r'^mapa/$', 'mapa', name='metas-mapa'),  # tagerror
    url(r'^mapdata/$', 'map_data', name='metas-map_data'),
    url(r'^mapsearch/$', 'map_search', name='metas-map_search'),
    url(r'^mapsum/$', 'map_sum', name='metas-map_sum'),
    url(r'^maplist/$', 'map_list', name='metas-map_list'),
)
