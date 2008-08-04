# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.convenios.models import Convenio, EquipamentoPrevisto, Anexo

class ConvenioAdmin(admin.ModelAdmin):
    ordering = ('-num_convenio',)
    list_display = ('num_convenio', 'casa_legislativa',
                    'num_processo_sf', 'data_adesao')
    list_filter  = ('equipamentos_recebidos',)

class EquipamentoPrevistoAdmin(admin.ModelAdmin):
    ordering = ('convenio', 'equipamento')
    list_display = ('convenio', 'equipamento', 'quantidade')
    list_display_links = ('convenio', 'equipamento')

class AnexoAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_pub'
    list_display = ('descricao', 'data_pub', 'convenio')

admin.site.register(Convenio, ConvenioAdmin)
admin.site.register(EquipamentoPrevisto, EquipamentoPrevistoAdmin)
admin.site.register(Anexo, AnexoAdmin)
