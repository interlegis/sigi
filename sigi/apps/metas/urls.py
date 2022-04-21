# coding: utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    "sigi.apps.metas.views",
    url(r"^$", "dashboard", name="metas-dashboardsss"),  # tagerror
    url(r"^openmap/$", "openmap", name="openmap"),
    url(r"^openmapdata/$", "openmapdata", name="openmapdata"),
    url(
        r"^openmapdetail/(?P<orgao_id>\w+)/$",
        "openmapdetail",
        name="openmapdetail",
    ),
    url(r"^openmapsearch/$", "openmapsearch", name="openmapsearch"),
)
