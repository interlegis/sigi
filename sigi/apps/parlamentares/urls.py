# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('sigi.apps.parlamentares.views',

	# Reports labels parlamentares
	url(r'^labels/$', 'labels_report', name='labels-report-all'),
	url(r'^(?P<id>\w+)/labels/$', 'labels_report', name='labels-report-id'),
)