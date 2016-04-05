# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('sigi.apps.home.views',
    url(r'^$', 'index', name='sigi_index'),
    url(r'^home/resumoconvenios/$', 'resumo_convenios', name="home_resumoconvenios"),
    url(r'^home/resumoseit/$', 'resumo_seit', name="home_resumoseit"),
    url(r'^home/chartseit/$', 'chart_seit', name="home_chartseit"),
    url(r'^home/chartconvenios/$', 'chart_convenios', name="home_chartconvenios"),
    url(r'^home/chartcarteira/$', 'chart_carteira', name="home_chartcarteira"),
    url(r'^home/chartperformance/$', 'chart_performance', name="home_chartperformance"),
    url(r'^home/report/semconvenio/$', 'report_sem_convenio', name="home_reportsemconvenio"),
    
)
