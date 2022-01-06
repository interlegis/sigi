from django.contrib import admin
from django.utils.translation import gettext as _

from sigi.apps.utils.filters import RangeFilter
from sigi.apps.contatos.models import (UnidadeFederativa, Mesorregiao,
                                       Microrregiao, Municipio, Telefone,
                                       Contato)
from sigi.apps.utils import queryset_ascii


class MesorregiaoInline(admin.TabularInline):
    model = Mesorregiao

class MicrorregiaoInline(admin.TabularInline):
    model = Microrregiao

@admin.register(UnidadeFederativa)
class UnidadeFederativaAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('codigo_ibge', 'nome', 'sigla', 'regiao', 'populacao')
    list_display_links = ('codigo_ibge', 'nome')
    list_filter = ('regiao', ('populacao', RangeFilter),)
    search_fields = ('search_text', 'codigo_ibge', 'sigla', 'regiao')
    get_queryset = queryset_ascii
    inlines = (MesorregiaoInline, )

@admin.register(Mesorregiao)
class MesorregiaoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('codigo_ibge', 'uf', 'nome')
    list_display_links = ('codigo_ibge', 'nome')
    list_filter = ('uf',)
    search_fields = ('uf__search_text', 'search_text', 'codigo_ibge',
                     'uf__sigla')
    get_queryset = queryset_ascii
    inlines = (MicrorregiaoInline,)

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('codigo_ibge', 'codigo_tse', 'nome', 'uf', 'is_capital',
                    'populacao', 'is_polo', 'idh', 'pib_ano', 'pib_total',
                    'pib_percapita')
    list_display_links = ('codigo_ibge', 'codigo_tse', 'nome')
    list_filter = ('is_capital', 'is_polo', ('idh', RangeFilter),
                   ('populacao', RangeFilter), 'uf__regiao', 'uf', )
    get_queryset = queryset_ascii
    fieldsets = (
        (None, {
            'fields': ('codigo_ibge', 'codigo_tse', 'nome', 'data_criacao',
                       'uf', 'microrregiao', 'is_capital', 'populacao',
                       'is_polo', 'idh', 'pib_ano', 'pib_total',
                       'pib_percapita')
        }),
        (_('Posição geográfica'), {
            'fields': ('latitude', 'longitude'),
        }),
    )
    search_fields = ('search_text', 'codigo_ibge', 'codigo_tse', 'uf__sigla')

@admin.register(Telefone)
class TelefoneAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'nota')
    list_display_links = ('numero',)
    list_filter = ('tipo',)
    radio_fields = {'tipo': admin.VERTICAL}
    search_fields = ('numero', 'tipo', 'nota')

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nota', 'email', 'municipio')
    list_display_links = ('nome',)
    list_filter = ('nome',)
    search_fields = ('nome', 'nota', 'email', 'municipio__nome',
                     'municipio__uf__nome')
