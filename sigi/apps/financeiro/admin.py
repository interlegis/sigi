# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.financeiro.models import Desembolso

class DesembolsoAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'descricao', 'data', 'valor_reais', 'valor_dolar',)
    fields = ('projeto', 'descricao', 'data', 'valor_reais', 'valor_dolar', )    
    list_filter = ('projeto',)
    date_hierarchy = 'data'