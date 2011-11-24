# -*- coding: utf8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'sigi.apps.diagnosticos.views.lista', name='lista_diagnosticos'),
)
