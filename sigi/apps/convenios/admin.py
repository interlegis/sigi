# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.convenios.models import Convenio, EquipamentoPrevisto, Anexo
from sigi.apps.servicos.models import Servico

class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub',]

class EquipamentoPrevistoInline(admin.TabularInline):
    model = EquipamentoPrevisto
    extra = 2
    raw_id_fields = ('equipamento',)

class AnexoAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_pub'
    exclude = ['data_pub',]
    list_display = ('arquivo', 'descricao', 'data_pub', 'convenio')
    raw_id_fields = ('convenio',)
    search_fields = ('descricao', 'convenio__num_convenio', 'arquivo',
                     'convenio__casa_legislativa__nome')

class ConvenioAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_adesao'
    fieldsets = (
        (None,
            {'fields': ('casa_legislativa', 'num_convenio', 'num_processo_sf',)}
        ),
        ('Datas',
            {'fields': ('data_adesao', 'data_retorno_assinatura',
                        'data_termo_aceite', 'data_pub_diario')}
        ),
        ('Equipamentos',
            {'fields': ('equipamentos_recebidos',)}
        )
    )
    inlines = (AnexosInline, EquipamentoPrevistoInline)
    list_display = ('num_convenio', 'casa_legislativa',
                    'num_processo_sf', 'data_adesao')
    list_filter  = ('equipamentos_recebidos',)
    ordering = ('-num_convenio',)
    raw_id_fields = ('casa_legislativa',)
    search_fields = ('num_convenio', 'casa_legislativa__nome',
                     'num_processo_sf', 'casa_legislativa__municipio__nome',
                     'casa_legislativa__municipio__uf__nome')

class EquipamentoPrevistoAdmin(admin.ModelAdmin):
    list_display = ('convenio', 'equipamento', 'quantidade')
    list_display_links = ('convenio', 'equipamento')
    ordering = ('convenio', 'equipamento')
    raw_id_fields = ('convenio', 'equipamento')
    search_fields = ('convenio__num_convenio', 'equipamento__fabricante__nome',
                     'equipamento__modelo__modelo', 'equipamento__modelo__tipo__tipo')

admin.site.register(Convenio, ConvenioAdmin)
admin.site.register(EquipamentoPrevisto, EquipamentoPrevistoAdmin)
admin.site.register(Anexo, AnexoAdmin)
