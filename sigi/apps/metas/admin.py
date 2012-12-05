# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.metas.models import Meta, PlanoDiretor

class MetaAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'titulo', 'data_inicio', 'data_fim', 'valor_meta', 'hora_ultimo_calculo', 'valor_ultimo_calculo', 
                    'percentual_concluido', 'saude',)
    fields = ('projeto', 'titulo', 'descricao', 'data_inicio', 'data_fim', 'algoritmo', 'valor_meta',)
    list_filter = ('projeto',)
    actions = ['recalcular',]
    
    def recalcular(self, request, queryset):
        for meta in queryset:
            meta.calcular()
        return None
    recalcular.short_description = u"Recalcular Metas BID selecionados"
    
class PlanoDiretorAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'casa_legislativa', 'status', 'data_elaboracao', 'data_assinatura', 'data_rejeicao',)
    fields = ('projeto', 'casa_legislativa', 'status', 'data_elaboracao', 'data_assinatura', 'data_rejeicao',)
    raw_id_fields = ('casa_legislativa',)
    list_filter = ('projeto', 'status',)