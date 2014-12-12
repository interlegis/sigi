# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('sigi.apps.saberes.views',
	url(r'^dashboard/$', 'dashboard', name="saberes-dashboard-view"),
	url(r'^dashboard/(?P<area>\w+)/$', 'detail', name="saberes-dashboard-detail"),
)