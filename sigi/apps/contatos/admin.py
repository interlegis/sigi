from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.utils.translation import gettext as _
from import_export import resources
from import_export.admin import ExportActionMixin
from sigi.apps.utils.filters import RangeFilter
from sigi.apps.contatos.models import (
    UnidadeFederativa,
    Mesorregiao,
    Microrregiao,
    Municipio,
    Telefone,
    Contato,
)
from sigi.apps.parlamentares.models import Senador
from sigi.apps.utils.mixins import AsciifyQParameter


class MicrorregiaoFilter(AutocompleteFilter):
    title = _("Microrregião")
    field_name = "microrregiao"


class UnidadeFederativaResource(resources.ModelResource):
    class Meta:
        model = UnidadeFederativa
        fields = ("codigo_ibge", "nome", "sigla", "regiao", "populacao")
        export_order = fields
        name = "Exportação de Unidades Federativas"

    def dehydrate_regiao(self, uf):
        return dict(UnidadeFederativa.REGIAO_CHOICES)[uf.regiao]


class MunicipioResource(resources.ModelResource):
    class Meta:
        model = Municipio
        fields = (
            "codigo_ibge",
            "codigo_tse",
            "nome",
            "uf__regiao",
            "uf__sigla",
            "uf__nome",
            "microrregiao__mesorregiao__nome",
            "microrregiao__nome",
            "is_capital",
            "populacao",
            "is_polo",
            "data_criacao",
            "latitude",
            "longitude",
            "idh",
            "pib_total",
            "pib_percapita",
            "pib_ano",
        )
        export_order = fields
        name = "Exportação de Municípios"

    def dehydrate_uf__regiao(self, municipio):
        return dict(UnidadeFederativa.REGIAO_CHOICES)[municipio.uf.regiao]


class MesorregiaoInline(admin.TabularInline):
    model = Mesorregiao


class MicrorregiaoInline(admin.TabularInline):
    model = Microrregiao


class SenadorInline(admin.StackedInline):
    model = Senador
    extra = 0
    autocomplete_fields = ("partido",)


@admin.register(UnidadeFederativa)
class UnidadeFederativaAdmin(
    AsciifyQParameter, ExportActionMixin, admin.ModelAdmin
):
    actions = None
    resource_classes = [UnidadeFederativaResource]
    list_display = ("codigo_ibge", "nome", "sigla", "regiao", "populacao")
    list_display_links = ("codigo_ibge", "nome")
    list_filter = (
        "regiao",
        ("populacao", RangeFilter),
    )
    search_fields = ("search_text", "codigo_ibge", "sigla", "regiao")
    inlines = (SenadorInline, MesorregiaoInline)


@admin.register(Mesorregiao)
class MesorregiaoAdmin(AsciifyQParameter, admin.ModelAdmin):
    actions = None
    list_display = ("codigo_ibge", "uf", "nome")
    list_display_links = ("codigo_ibge", "nome")
    list_filter = ("uf",)
    search_fields = (
        "uf__search_text",
        "search_text",
        "codigo_ibge",
        "uf__sigla",
    )
    autocomplete_fields = ("uf",)
    inlines = (MicrorregiaoInline,)


@admin.register(Microrregiao)
class MicrorregiaoAdmin(AsciifyQParameter, admin.ModelAdmin):
    search_fields = ("search_text",)


@admin.register(Municipio)
class MunicipioAdmin(AsciifyQParameter, ExportActionMixin, admin.ModelAdmin):
    actions = None
    resource_classes = [MunicipioResource]
    list_display = (
        "codigo_ibge",
        "codigo_tse",
        "nome",
        "uf",
        "get_regiao",
        "microrregiao",
        "is_capital",
        "populacao",
        "is_polo",
        "idh",
        "pib_ano",
        "pib_total",
        "pib_percapita",
    )
    list_display_links = ("codigo_ibge", "codigo_tse", "nome")
    list_filter = (
        "uf",
        "is_capital",
        "is_polo",
        ("idh", RangeFilter),
        ("populacao", RangeFilter),
        "uf__regiao",
        MicrorregiaoFilter,
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "codigo_ibge",
                    "codigo_tse",
                    "nome",
                    "data_criacao",
                    "uf",
                    "microrregiao",
                    "is_capital",
                    "populacao",
                    "is_polo",
                    "idh",
                    "pib_ano",
                    "pib_total",
                    "pib_percapita",
                )
            },
        ),
        (
            _("Posição geográfica"),
            {
                "fields": ("latitude", "longitude"),
            },
        ),
    )
    autocomplete_fields = ("uf", "microrregiao")
    search_fields = ("search_text", "codigo_ibge", "codigo_tse", "uf__sigla")

    @admin.display(description=_("Região"), ordering="uf__regiao")
    def get_regiao(self, obj):
        return obj.uf.get_regiao_display()


@admin.register(Telefone)
class TelefoneAdmin(admin.ModelAdmin):
    list_display = ("numero", "tipo", "nota")
    list_display_links = ("numero",)
    list_filter = ("tipo",)
    radio_fields = {"tipo": admin.VERTICAL}
    search_fields = ("numero", "tipo", "nota")


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ("nome", "nota", "email", "municipio")
    list_display_links = ("nome",)
    list_filter = ("nome",)
    search_fields = (
        "nome",
        "nota",
        "email",
        "municipio__nome",
        "municipio__uf__nome",
    )
