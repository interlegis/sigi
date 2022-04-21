# -*- coding: utf-8 -*-
from django.contrib import admin

from sigi.apps.financeiro.models import Desembolso
from sigi.apps.utils.base_admin import BaseModelAdmin


class DesembolsoAdmin(BaseModelAdmin):
    list_display = (
        "projeto",
        "descricao",
        "data",
        "valor_reais",
        "valor_dolar",
    )
    fields = (
        "projeto",
        "descricao",
        "data",
        "valor_reais",
        "valor_dolar",
    )
    list_filter = ("projeto",)
    date_hierarchy = "data"


admin.site.register(Desembolso, DesembolsoAdmin)
