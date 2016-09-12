# coding: utf-8
from django.conf.urls import url
from sigi.apps.metas import views


urlpatterns = [
    url(r'^$', views.dashboard, name='metas-dashboardsss'),  # tagerror
    url(r'^mapa/$', views.mapa, name='metas-mapa'),  # tagerror
    url(r'^mapdata/$', views.map_data, name='metas-map_data'),
    url(r'^mapsearch/$', views.map_search, name='metas-map_search'),
    url(r'^mapsum/$', views.map_sum, name='metas-map_sum'),
    url(r'^maplist/$', views.map_list, name='metas-map_list'),
]
