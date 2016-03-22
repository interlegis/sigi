# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('sigi.apps.home.views',
    url(r'^$', 'index', name='sigi_index'),
)
