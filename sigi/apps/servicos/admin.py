from django.contrib import admin
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import gettext as _
from import_export.fields import Field
from sigi.apps.casas.admin import GerentesInterlegisFilter
from sigi.apps.servicos.models import Servico, LogServico, TipoServico
from sigi.apps.servicos.filters import (
    ServicoAtivoFilter,
    DataUtimoUsoFilter,
)
from sigi.apps.convenios.filters import (
    TipoProjetoFilter,
    ExcluirTipoProjetoFilter,
)
from sigi.apps.utils.filters import DateRangeFilter
from sigi.apps.utils.mixins import (
    ReturnMixin,
    CartExportMixin,
    ValueLabeledResource,
)


class ServicoExportResourse(ValueLabeledResource):
    hospedagem_interlegis = Field(column_name="hospedagem no interlegis")

    class Meta:
        model = Servico
        fields = (
            "casa_legislativa__nome",
            "casa_legislativa__municipio__nome",
            "casa_legislativa__municipio__uf__sigla",
            "casa_legislativa__email",
            "casa_legislativa__telefone_geral",
            "tipo_servico__nome",
            "url",
            "hospedagem_interlegis",
            "data_ativacao",
            "data_desativacao",
            "motivo_desativacao",
            "data_ultimo_uso",
            "erro_atualizacao",
            "casa_legislativa__convenio__projeto__sigla",
            "casa_legislativa__convenio__num_convenio",
            "casa_legislativa__convenio__num_processo_sf",
            "casa_legislativa__convenio__data_retorno_assinatura",
            "casa_legislativa__convenio__data_termino_vigencia",
        )
        export_order = fields

    def dehydrate_hospedagem_interlegis(self, servico):
        if servico["hospedagem_interlegis"]:
            return _("Sim")
        else:
            return _("Não")


class LogServicoInline(admin.StackedInline):
    model = LogServico
    Fieldset = (None, {"fields": (("data", "descricao"), "log")})
    extra = 1


@admin.register(TipoServico)
class TipoServicoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sigla",
        "nome",
        "qtde_casas_atendidas",
    )
    ordering = ["id"]
    list_display_links = ["id", "sigla"]


@admin.register(Servico)
class ServicoAdmin(ReturnMixin, CartExportMixin, admin.ModelAdmin):
    actions = [
        "calcular_data_uso",
    ]
    list_display = (
        "tipo_servico",
        "versao",
        "casa_legislativa",
        "get_uf",
        "hospedagem_interlegis",
        "data_ativacao",
        "data_desativacao",
        "getUrl",
        "data_verificacao",
        "resultado_verificacao",
        "data_ultimo_uso",
        "get_link_erro",
    )
    fields = [
        "casa_legislativa",
        "tipo_servico",
        "versao",
        "url",
        "hospedagem_interlegis",
        "instancia",
        "data_ativacao",
        "data_alteracao",
        "data_desativacao",
        "motivo_desativacao",
    ]
    autocomplete_fields = ("casa_legislativa",)
    readonly_fields = ["data_alteracao"]
    list_filter = (
        "tipo_servico",
        "hospedagem_interlegis",
        ("data_ativacao", DateRangeFilter),
        ("data_desativacao", ServicoAtivoFilter),
        "resultado_verificacao",
        DataUtimoUsoFilter,
        ("casa_legislativa__gerentes_interlegis", GerentesInterlegisFilter),
        "casa_legislativa__municipio__uf",
        ("casa_legislativa__convenio__projeto_id", TipoProjetoFilter),
        ("casa_legislativa__convenio__projeto_id", ExcluirTipoProjetoFilter),
    )
    ordering = (
        "casa_legislativa__municipio__uf",
        "casa_legislativa",
        "tipo_servico",
    )
    inlines = (LogServicoInline,)
    search_fields = ("casa_legislativa__search_text",)
    resource_class = ServicoExportResourse

    def get_uf(self, obj):
        return "%s" % (obj.casa_legislativa.municipio.uf)

    get_uf.short_description = _("UF")
    get_uf.admin_order_field = "casa_legislativa__municipio__uf"

    def getUrl(self, obj):
        url = obj.url
        if "//" not in url:
            url = "//" + url
        return mark_safe(f'<a href="{url}" target="_blank">{obj.url}</a>')

    getUrl.short_description = _("Url")

    def get_link_erro(self, obj):
        if not obj.erro_atualizacao:
            return ""
        url = obj.url
        if url[-1] != "/":
            url += "/"
        if obj.tipo_servico.string_pesquisa:
            url += obj.tipo_servico.string_pesquisa.splitlines()[0].split(" ")[
                0
            ]
        elif obj.tipo_servico.modo == "R":
            url = f"https://toolbox.googleapps.com/apps/dig/#SOA/{obj.url}"
        return mark_safe(
            f'<a href="{url}" target="_blank">{obj.erro_atualizacao}</a>'
        )

    get_link_erro.short_description = _("Erro na atualização")
    get_link_erro.admin_order_field = "erro_atualizacao"

    def calcular_data_uso(self, request, queryset):
        for servico in queryset:
            servico.atualiza_data_uso()
        self.message_user(
            request,
            _(
                "Atualização concluída. Os sites que não "
                "responderam foram deixados com a data "
                "em branco"
            ),
        )
        return HttpResponseRedirect(".")

    calcular_data_uso.short_description = _(
        "Atualizar a data do último uso do(s) serviço(s)"
    )

    def lookup_allowed(self, lookup, value):
        return super(ServicoAdmin, self).lookup_allowed(
            lookup, value
        ) or lookup in [
            "casa_legislativa__municipio__uf__codigo_ibge__exact",
        ]

    def changelist_view(self, request, extra_context=None):
        from sigi.apps.convenios.views import normaliza_data

        request.GET._mutable = True
        normaliza_data(request.GET, "data_ativacao__gte")
        normaliza_data(request.GET, "data_ativacao__lte")
        request.GET._mutable = False

        return super(ServicoAdmin, self).changelist_view(
            request,
            extra_context={"query_str": "?" + request.META["QUERY_STRING"]},
        )
