# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.contatos.models import (UnidadeFederativa, Municipio, Telefone,
                                       Contato)

class UnidadeFederativaAdmin(admin.ModelAdmin):
    list_display = ('codigo_ibge', 'nome', 'sigla', 'regiao', 'populacao')
    list_display_links = ('codigo_ibge', 'nome')
    list_filter = ('regiao', 'populacao')
    search_fields = ('codigo_ibge', 'nome', 'sigla', 'regiao')

class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('codigo_ibge', 'nome', 'uf', 'is_capital', 'populacao', 'is_polo')
    list_display_links = ('codigo_ibge', 'nome')
    list_filter = ('is_capital', 'is_polo', 'populacao', 'uf')
    fieldsets = (
        (None, {
            'fields': ('codigo_ibge', 'codigo_mesorregiao',
                       'codigo_microrregiao', 'nome', 'uf', 'is_capital',
                       'populacao', 'is_polo')
        }),
        ('Posição geográfica', {
            'fields': ('latitude', 'longitude'),
        }),
    )
    search_fields = ('codigo_ibge', 'codigo_mesorregiao', 'codigo_microrregiao',
                     'nome', 'uf__nome', 'uf__sigla')

class TelefoneAdmin(admin.ModelAdmin):
    list_display = ('codigo_area', 'numero', 'tipo', 'nota')
    list_display_links = ('codigo_area', 'numero')
    list_filter = ('codigo_area', 'tipo')
    radio_fields = {'tipo': admin.VERTICAL}
    search_fields = ('codigo_area', 'numero', 'tipo', 'nota')

class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nota', 'email', 'municipio', 'get_uf')
    list_display_links = ('nome',)
    list_filter = ('nome',)
    search_fields = ('nome', 'nota', 'email', 'municipio__nome', 'municipio__uf__nome')

    def get_uf(self, obj):
        return obj.municipio.uf.nome
    get_uf.short_description = 'UF'

admin.site.register(UnidadeFederativa, UnidadeFederativaAdmin)
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(Telefone, TelefoneAdmin)
admin.site.register(Contato, ContatoAdmin)
