# coding: utf-8
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from sigi.apps.home import views

urlpatterns = [
    url(r'^atendimento', TemplateView.as_view(
        template_name='index_atendimento.html'),
        name='index_atendimento'),
    url(r'^$', views.index, name='sigi_index'),
    url(r'^home/resumoconvenios/$', views.resumo_convenios,
        name="home_resumoconvenios"),
    url(r'^home/resumoseit/$', views.resumo_seit, name="home_resumoseit"),
    url(r'^home/chartseit/$', views.chart_seit, name="home_chartseit"),
    url(r'^home/chartconvenios/$', views.chart_convenios,
        name="home_chartconvenios"),
    url(r'^home/chartcarteira/$', views.chart_carteira, name="home_chartcarteira"),
    url(r'^home/chartperformance/$', views.chart_performance,
        name="home_chartperformance"),
    url(r'^home/report/semconvenio/$', views.report_sem_convenio,
        name="home_reportsemconvenio"),
]
