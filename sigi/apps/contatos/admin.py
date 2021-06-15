from django.contrib import admin
from django.utils.translation import ugettext as _

from sigi.apps.contatos.models import (UnidadeFederativa, Mesorregiao,
                                       Microrregiao, Municipio)
from sigi.apps.utils import queryset_ascii
from sigi.apps.utils.filters import (MultiChoicesFieldListFilter,
                                     MultiRelatedFieldListFilter,
                                     RangeFieldListFilter)

class MesorregiaoInline(admin.TabularInline):
    model = Mesorregiao

class MicrorregiaoInline(admin.TabularInline):
    model = Microrregiao

@admin.register(UnidadeFederativa)
class UnidadeFederativaAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('codigo_ibge', 'nome', 'sigla', 'regiao', 'populacao')
    list_display_links = ('codigo_ibge', 'nome')
    list_filter = (
        ('regiao', MultiChoicesFieldListFilter),
        ('populacao', RangeFieldListFilter),
    )
    search_fields = ('search_text', 'codigo_ibge', 'sigla', 'regiao')
    queryset = queryset_ascii
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
    list_filter = ('is_capital', 'is_polo', ('idh', RangeFieldListFilter),
                   ('populacao', RangeFieldListFilter),
                   ('uf', MultiRelatedFieldListFilter),
                   ('uf__regiao', MultiChoicesFieldListFilter))
    get_queryset = queryset_ascii
    fieldsets = (
        (None, {
            'fields': ('codigo_ibge', 'codigo_tse', 'nome', 'data_criacao',
                       'uf', 'microrregiao', 'is_capital', 'populacao',
                       'is_polo', 'idh', 'pib_ano', 'pib_total',
                       'pib_percapita')
        }),
        (_(u'Posição geográfica'), {
            'fields': ('latitude', 'longitude'),
        }),
    )
    search_fields = ('search_text', 'codigo_ibge', 'codigo_tse', 'uf__sigla')