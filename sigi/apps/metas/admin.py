# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.metas.models import Meta, PlanoDiretor

class MetaAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'titulo', 'data_inicio', 'data_fim', 'valor_meta', 'valor_executado', 'percentual_concluido',)
    fields = ('projeto', 'titulo', 'descricao', 'data_inicio', 'data_fim', 'algoritmo', 'valor_meta',)
    list_filter = ('projeto',)
        
class PlanoDiretorAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'casa_legislativa', 'status', 'data_entrega', 'data_implantacao',)
    fields = ('projeto', 'casa_legislativa', 'status', 'data_entrega', 'data_implantacao',)
    raw_id_fields = ('casa_legislativa',)
    list_filter = ('projeto', 'status',)