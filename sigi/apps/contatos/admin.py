# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.contatos.models import (UnidadeFederativa, Municipio, Telefone,
                                       Contato)

class UnidadeFederativaAdmin(admin.ModelAdmin):
    list_display = ('codigo_ibge', 'nome', 'sigla')
    list_display_links = ('codigo_ibge', 'nome', 'sigla')
    search_fields = ('codigo_ibge', 'nome', 'sigla')

class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('codigo_ibge', 'nome', 'uf')
    list_display_links = ('codigo_ibge', 'nome')
    list_filter = ('uf',)
    search_fields = ('codigo_ibge', 'nome', 'uf')

class TelefoneAdmin(admin.ModelAdmin):
    list_display = ('codigo_ddd', 'numero', 'tipo', 'nota')
    list_display_links = ('codigo_ddd', 'numero')
    list_filter = ('codigo_ddd',)
    radio_fields = {'tipo': admin.VERTICAL}
    search_fields = ('codigo_ddd', 'numero', 'tipo', 'nota')

class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nota')
    list_display_links = ('nome',)

admin.site.register(UnidadeFederativa, UnidadeFederativaAdmin)
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(Telefone, TelefoneAdmin)
admin.site.register(Contato, ContatoAdmin)
