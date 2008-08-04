# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.mesas.models import (Legislatura, Coligacao, ComposicaoColigacao,
                                    SessaoLegislativa, MesaDiretora, Cargo,
                                    MembroMesaDiretora)

class LegislaturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'data_inicio', 'data_fim', 'data_eleicao')
    list_display_links = ('numero',)

class ColigacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'legislatura', 'numero_votos')
    list_display_links = ('nome',)
    search_fields = ('nome',)

class ComposicaoColigacaoAdmin(admin.ModelAdmin):
    list_display = ('coligacao', 'partido')
    list_display_links = ('coligacao', 'partido')
    list_filter = ('partido',)

class SessaoLegislativaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'mesa_diretora', 'legislatura', 'tipo',
                    'data_inicio', 'data_fim')
    list_display_links = ('numero',)
    list_filter = ('tipo',)
    radio_fields = {'tipo': admin.VERTICAL}

class CargoAdmin(admin.ModelAdmin):
    list_display = ('descricao',)

class MembroMesaDiretoraInline(admin.TabularInline):
    model = MembroMesaDiretora
    max_num = 11
    extra = 4

class MembroMesaDiretoraAdmin(admin.ModelAdmin):
    list_display = ('parlamentar', 'cargo')
    list_display_links = ('parlamentar', 'cargo')
    list_filter = ('cargo',)
    search_fields = ('parlamentar', 'cargo')

class MesaDiretoraAdmin(admin.ModelAdmin):
    inlines = (MembroMesaDiretoraInline,)
    list_display = ('id', 'casa_legislativa')

admin.site.register(Legislatura, LegislaturaAdmin)
admin.site.register(Coligacao, ColigacaoAdmin)
admin.site.register(ComposicaoColigacao, ComposicaoColigacaoAdmin)
admin.site.register(SessaoLegislativa, SessaoLegislativaAdmin)
admin.site.register(MesaDiretora, MesaDiretoraAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(MembroMesaDiretora, MembroMesaDiretoraAdmin)
