# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.servicos.models import Servico

class ServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'situacao', 'avaliacao')
    list_filter  = ('situacao', 'avaliacao',)

admin.site.register(Servico, ServicoAdmin)
