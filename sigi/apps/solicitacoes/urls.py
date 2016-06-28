from __future__ import absolute_import

from django.conf.urls import include, url

from sigi.apps.solicitacoes.views import SolicitacaoCrud

from .apps import AppConfig

app_name = AppConfig.name

urlpatterns = [
    url(ur'atendimento/solicitacao/',
        include(SolicitacaoCrud.get_urls())),
]
