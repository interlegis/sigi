# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.convenios.models import Projeto, Convenio, EquipamentoPrevisto, Anexo
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
    search_fields = ('descricao', 'convenio__id', 'arquivo',
                     'convenio__casa_legislativa__nome')

class ConvenioAdmin(admin.ModelAdmin):
    change_list_template = 'convenios/change_list.html'
    fieldsets = (
        (None,
            {'fields': ('casa_legislativa', 'num_processo_sf','projeto')}
        ),
        ('Datas',
            {'fields': ('data_adesao', 'data_retorno_assinatura',
                        'data_termo_aceite', 'data_pub_diario',
                        'data_devolucao_via', 'data_postagem_correio')}
        ),
    )
    inlines = (AnexosInline, EquipamentoPrevistoInline)
    list_display = ('id', 'casa_legislativa',
                    'num_processo_sf', 'data_adesao')
    list_filter  = ('data_adesao', 'data_retorno_assinatura',
                    'data_termo_aceite', 'data_devolucao_via',
                    'data_postagem_correio')
    ordering = ('-id',)
    raw_id_fields = ('casa_legislativa',)
    search_fields = ('id', 'casa_legislativa__nome',
                     'num_processo_sf', 'casa_legislativa__municipio__nome',
                     'casa_legislativa__municipio__uf__nome')

class EquipamentoPrevistoAdmin(admin.ModelAdmin):
    list_display = ('convenio', 'equipamento', 'quantidade')
    list_display_links = ('convenio', 'equipamento')
    ordering = ('convenio', 'equipamento')
    raw_id_fields = ('convenio', 'equipamento')
    search_fields = ('convenio__id', 'equipamento__fabricante__nome',
                     'equipamento__modelo__modelo', 'equipamento__modelo__tipo__tipo')

admin.site.register(Projeto)
admin.site.register(Convenio, ConvenioAdmin)
admin.site.register(EquipamentoPrevisto, EquipamentoPrevistoAdmin)
admin.site.register(Anexo, AnexoAdmin)
