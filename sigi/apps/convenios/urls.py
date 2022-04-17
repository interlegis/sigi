from django.urls import path
from sigi.apps.convenios import views

urlpatterns = [
    path('reportsRegiao/<str:regiao>/', views.report_regiao, name='convenios-report_regiao_pdf'),
    path('importar/', views.importar_gescon, name='importar-gescon'),
]

# urlpatterns = patterns(
#     'sigi.apps.convenios.views',

#     url(r'^convenio/reports/$', 'report', name='convenios-report'),
#     url(r'^convenio/carrinho/$', 'visualizar_carrinho', name='visualizar-carrinho'),
#     url(r'^convenio/carrinho/excluir_carrinho/$', 'excluir_carrinho', name='excluir-carrinho'),  # tagerror
#     url(r'^convenio/carrinho/deleta_itens_carrinho$', 'deleta_itens_carrinho', name='deleta-itens-carrinho'),  # tagerror
#     url(r'^convenio/csv/$', 'export_csv', name='convenios-csv'),
#     url(r'^importar/$', 'importar_gescon', name='importar-gescon'),
# )
