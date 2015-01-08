# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _

from sigi.apps.contatos.filters import PopulationFilter
from sigi.apps.contatos.models import (UnidadeFederativa, Municipio, Telefone,
                                       Contato)
from sigi.apps.utils import queryset_ascii
from sigi.apps.utils.base_admin import BaseModelAdmin


class UnidadeFederativaAdmin(BaseModelAdmin):
    actions = None
    list_display = ('codigo_ibge', 'nome', 'sigla', 'regiao', 'populacao')
    list_display_links = ('codigo_ibge', 'nome')
    list_filter = ('regiao', 'populacao', PopulationFilter,)
    search_fields = ('search_text', 'codigo_ibge', 'sigla', 'regiao')
    get_queryset = queryset_ascii


class MunicipioAdmin(BaseModelAdmin):
    actions = None
    list_display = ('codigo_ibge', 'codigo_tse', 'nome', 'uf', 'is_capital', 'populacao', 'is_polo', 'idh', 'pib_ano',
                    'pib_total', 'pib_percapita')
    list_display_links = ('codigo_ibge', 'codigo_tse', 'nome')
    list_filter = ('is_capital', 'is_polo', 'idh', 'populacao', 'uf', )
    get_queryset = queryset_ascii
    fieldsets = (
        (None, {
            'fields': ('codigo_ibge', 'codigo_tse', 'codigo_mesorregiao',
                       'codigo_microrregiao', 'nome', 'data_criacao', 'uf',
                       'is_capital', 'populacao', 'is_polo', 'idh', 'pib_ano', 'pib_total', 'pib_percapita')
        }),
        (_(u'Posição geográfica'), {
            'fields': ('latitude', 'longitude'),
        }),
    )
    search_fields = ('search_text', 'codigo_ibge', 'codigo_tse', 'codigo_mesorregiao',
                     'codigo_microrregiao', 'uf__sigla')


class TelefoneAdmin(BaseModelAdmin):
    list_display = ('numero', 'tipo', 'nota')
    list_display_links = ('numero',)
    list_filter = ('tipo',)
    radio_fields = {'tipo': admin.VERTICAL}
    search_fields = ('numero', 'tipo', 'nota')


class ContatoAdmin(BaseModelAdmin):
    list_display = ('nome', 'nota', 'email', 'municipio')
    list_display_links = ('nome',)
    list_filter = ('nome',)
    search_fields = ('nome', 'nota', 'email', 'municipio__nome', 'municipio__uf__nome')

admin.site.register(UnidadeFederativa, UnidadeFederativaAdmin)
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(Telefone, TelefoneAdmin)
admin.site.register(Contato, ContatoAdmin)
