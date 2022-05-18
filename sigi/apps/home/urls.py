from django.urls import path
from sigi.apps.home import views

urlpatterns = [
    path("", views.openmap, name="openmap"),
    path("openmapdata/", views.openmapdata, name="openmapdata"),
    path(
        "openmapdetail/<orgao_id>/", views.openmapdetail, name="openmapdetail"
    ),
    path("openmapsearch/", views.openmapsearch, name="openmapsearch"),
    path("home/resumoseit/", views.resumo_seit, name="home_resumoseit"),
    path("home/chartseit/", views.chart_seit, name="home_chartseit"),
    path(
        "home/chartusoservico/",
        views.chart_uso_servico,
        name="home_chartusoservico",
    ),
    path(
        "home/chartatualizacao/",
        views.chart_atualizacao_servicos,
        name="home_chartatualizacao",
    ),
    path(
        "home/chartperformance/",
        views.chart_performance,
        name="home_chartperformance",
    ),
    path(
        "home/chartcarteira/", views.chart_carteira, name="home_chartcarteira"
    ),
    path(
        "home/resumoconvenios/",
        views.resumo_convenios,
        name="home_resumoconvenios",
    ),
    path(
        "home/report/semconvenio/",
        views.report_sem_convenio,
        name="home_reportsemconvenio",
    ),
    path(
        "home/dashboard/card/<slug:card_code>/",
        views.card_snippet,
        name="home_cardsnippet",
    ),
    path(
        "home/dashboard/addtab/<slug:tab_slug>/",
        views.card_add_tab,
        name="home_card_add_tab",
    ),
    path(
        "home/dashboard/changetab/",
        views.card_rename_tab,
        name="home_card_rename_tab",
    ),
    path(
        "home/dashboard/reorder/",
        views.card_reorder,
        name="home_card_reorder",
    ),
    path(
        "home/dashboard/remove/<categoria>/<slug:codigo>/",
        views.card_remove,
        name="home_card_remove",
    ),
    path("home/dashboard/addcard/", views.card_add, name="home_add_card"),
]

# from django.conf.urls import patterns, url


# urlpatterns = patterns('sigi.apps.home.views',
#     url(r'^$', 'index', name='sigi_index'),
#     url(r'^home/chartseit/$', 'chart_seit', name="home_chartseit"),
#     url(r'^home/chartconvenios/$', 'chart_convenios', name="home_chartconvenios"),
#     url(r'^home/chartcarteira/$', 'chart_carteira', name="home_chartcarteira"),
#     url(r'^home/chartperformance/$', 'chart_performance', name="home_chartperformance"),
#     url(r'^home/report/semconvenio/$', 'report_sem_convenio', name="home_reportsemconvenio"),

# )
