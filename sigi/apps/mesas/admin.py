# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.mesas.models import (Legislatura, Coligacao, ComposicaoColigacao,
                                    SessaoLegislativa, MesaDiretora, Cargo,
                                    MembroMesaDiretora)

class LegislaturaAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_inicio'
    list_display = ('numero', 'data_inicio', 'data_fim', 'data_eleicao')
    list_display_links = ('numero',)
    search_fields = ('numero',)

class ColigacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'legislatura', 'numero_votos')
    list_display_links = ('nome',)
    search_fields = ('nome', 'legislatura__numero')

class ComposicaoColigacaoAdmin(admin.ModelAdmin):
    list_display = ('coligacao', 'partido')
    list_display_links = ('coligacao', 'partido')
    list_filter = ('partido',)
    search_fields = ('coligacao__nome', 'partido__nome', 'partido__sigla')

class SessaoLegislativaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'mesa_diretora', 'legislatura', 'tipo',
                    'data_inicio', 'data_fim')
    list_display_links = ('numero',)
    list_filter = ('tipo',)
    fieldsets = (
        (None, {
            'fields': ('numero', 'mesa_diretora', 'legislatura', 'tipo')
        }),
        (None, {
            'fields': (('data_inicio', 'data_fim'),
                       ('data_inicio_intervalo', 'data_fim_intervalo'))
        }),
    )
    radio_fields = {'tipo': admin.VERTICAL}
    search_fields = ('numero', 'mesa_diretora__casa_legislativa__nome')

class CargoAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    search_fields = ('descricao',)

class MembroMesaDiretoraInline(admin.TabularInline):
    model = MembroMesaDiretora
    max_num = 11
    extra = 4

class MembroMesaDiretoraAdmin(admin.ModelAdmin):
    list_display = ('parlamentar', 'cargo', 'mesa_diretora')
    list_display_links = ('parlamentar',)
    list_filter = ('cargo',)
    search_fields = ('cargo__descricao', 'parlamentar__nome_completo',
                     'parlamentar__nome_parlamentar',
                     'mesa_diretora__casa_legislativa__nome')

class MesaDiretoraAdmin(admin.ModelAdmin):
    inlines = (MembroMesaDiretoraInline,)
    list_display = ('id', 'casa_legislativa')
    search_fields = ('casa_legislativa__nome',)

admin.site.register(Legislatura, LegislaturaAdmin)
admin.site.register(Coligacao, ColigacaoAdmin)
admin.site.register(ComposicaoColigacao, ComposicaoColigacaoAdmin)
admin.site.register(SessaoLegislativa, SessaoLegislativaAdmin)
admin.site.register(MesaDiretora, MesaDiretoraAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(MembroMesaDiretora, MembroMesaDiretoraAdmin)
