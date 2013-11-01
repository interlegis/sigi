# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('sigi.apps.convenios.views',
	url(r'^reports/$', 'report', name='convenios-report'),
)