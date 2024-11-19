from django.db.models import Q
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django_weasyprint.views import WeasyTemplateResponse
from import_export import resources
from import_export.admin import ExportActionMixin
from tinymce.models import HTMLField
from tinymce.widgets import AdminTinyMCE
from sigi.apps.convenios.models import (
    Projeto,
    StatusConvenio,
    TipoSolicitacao,
    Convenio,
    EquipamentoPrevisto,
    Anexo,
    Gescon,
)
from sigi.apps.utils.mixins import AsciifyQParameter
from sigi.apps.casas.admin import GerentesInterlegisFilter
from sigi.apps.utils.mixins import ReturnMixin
from sigi.apps.utils.filters import DateRangeFilter


class ConvenioExportResourse(resources.ModelResource):
    class Meta:
        model = Convenio
        fields = (
            "num_processo_sf",
            "num_convenio",
            "projeto__nome",
            "casa_legislativa__nome",
            "casa_legislativa__municipio__nome",
            "casa_legislativa__municipio__uf__sigla",
            "data_sigi",
            "data_sigad",
            "data_adesao",
            "data_retorno_assinatura",
            "data_solicitacao",
            "atualizacao_gescon",
            "observacao_gescon",
            "tipo_solicitacao__nome",
            "status__nome",
            "acompanha__nome_completo",
            "servidor_gestao__nome_completo",
            "observacao",
        )
        export_order = fields


class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = [
        "data_pub",
    ]


class AnexoAdmin(admin.ModelAdmin):
    date_hierarchy = "data_pub"
    exclude = [
        "data_pub",
    ]
    list_display = ("arquivo", "descricao", "data_pub", "convenio")
    autocomplete_fields = ("convenio",)
    search_fields = (
        "descricao",
        "convenio__id",
        "arquivo",
        "convenio__casa_legislativa__nome",
    )


class ConvenioVigenteFilter(admin.filters.SimpleListFilter):
    parameter_name = "vigencia"
    title = _("Vigência")

    def lookups(self, request, model_admin):
        return (
            ("vigentes", _("Vigentes")),
            ("vencidos", _("Vencidos")),
            ("pendentes", _("Pendentes")),
        )

    def queryset(self, request, queryset):
        if self.value() == "vigentes":
            return queryset.filter(
                Q(data_termino_vigencia__gte=timezone.localdate())
                | Q(data_termino_vigencia=None)
            ).exclude(data_retorno_assinatura=None)
        elif self.value() == "vencidos":
            return queryset.exclude(data_termino_vigencia=None).filter(
                data_termino_vigencia__lt=timezone.localdate()
            )
        elif self.value() == "pendentes":
            return queryset.filter(
                data_retorno_assinatura=None,
                data_devolucao_sem_assinatura=None,
                data_retorno_sem_assinatura=None,
            )
        return queryset


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("sigla", "nome")
    formfield_overrides = {HTMLField: {"widget": AdminTinyMCE}}


@admin.register(Convenio)
class ConvenioAdmin(
    AsciifyQParameter, ReturnMixin, ExportActionMixin, admin.ModelAdmin
):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "casa_legislativa",
                    "num_processo_sf",
                    "num_convenio",
                    "projeto",
                    "data_sigi",
                )
            },
        ),
        (
            _("Acompanhamento no gabinete"),
            {
                "fields": (
                    "data_solicitacao",
                    "data_sigad",
                    "observacao",
                )
            },
        ),
        (
            _("Gestão do convênio"),
            {
                "fields": (
                    "servico_gestao",
                    "servidor_gestao",
                )
            },
        ),
        (
            _("Datas"),
            {
                "fields": (
                    "data_retorno_assinatura",
                    "data_termino_vigencia",
                    "data_pub_diario",
                )
            },
        ),
        (
            _("Extinção / desistência"),
            {
                "fields": (
                    "data_extincao",
                    "motivo_extincao",
                )
            },
        ),
        (
            _("Gescon"),
            {
                "fields": (
                    "erro_gescon",
                    "atualizacao_gescon",
                    "observacao_gescon",
                    "link_gescon",
                )
            },
        ),
    )
    readonly_fields = (
        "data_sigi",
        "erro_gescon",
        "atualizacao_gescon",
        "observacao_gescon",
        "link_gescon",
    )
    inlines = (AnexosInline,)
    list_display = (
        "num_convenio",
        "projeto",
        "casa_legislativa",
        "get_uf",
        "status_convenio",
        "link_sigad",
        "data_retorno_assinatura",
        "data_termino_vigencia",
    )
    list_display_links = (
        "num_convenio",
        "casa_legislativa",
    )
    list_filter = (
        ("data_retorno_assinatura", DateRangeFilter),
        ("data_termino_vigencia", DateRangeFilter),
        ConvenioVigenteFilter,
        ("casa_legislativa__gerentes_interlegis", GerentesInterlegisFilter),
        "projeto",
        "casa_legislativa__tipo",
        "conveniada",
        "equipada",
        "casa_legislativa__municipio__uf",
        "erro_gescon",
    )
    ordering = (
        "casa_legislativa__municipio__uf__sigla",
        "casa_legislativa",
        "-data_retorno_assinatura",
    )
    autocomplete_fields = (
        "casa_legislativa",
        "servico_gestao",
        "servidor_gestao",
    )
    search_fields = (
        "id",
        "casa_legislativa__search_text",
        "casa_legislativa__sigla",
        "num_processo_sf",
        "num_convenio",
    )
    resource_class = ConvenioExportResourse
    reports = [
        "report_convenios",
    ]

    def get_uf(self, obj):
        return obj.casa_legislativa.municipio.uf.sigla

    get_uf.short_description = _("UF")
    get_uf.admin_order_field = "casa_legislativa__municipio__uf__sigla"

    def status_convenio(self, obj):
        if obj.pk is None:
            return ""
        status = obj.get_status()

        if status in ["Vencido", "Desistência", "Cancelado", "Extinto"]:
            label = r"danger"
        elif status == "Vigente":
            label = r"success"
        elif status == "Pendente":
            label = r"warning"
        else:
            label = r"info"
        return mark_safe(f'<p class="label label-{label}">{status}</p>')

    status_convenio.short_description = _("Status do convênio")

    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return mark_safe(obj.get_sigad_url())

    link_sigad.short_description = _("Processo no Senado")

    def link_gescon(self, obj):
        if not obj.id_contrato_gescon:
            return ""
        return mark_safe(
            f"<a href='{obj.get_url_gescon()}'>{obj.id_contrato_gescon}</a>"
        )

    link_gescon.short_description = _("Download MINUTA ASSINADA do Gescon")

    def report_convenios(self, request):
        context = {
            "convenios": self.get_queryset(request).order_by(
                "casa_legislativa__tipo",
                "casa_legislativa__municipio__uf__sigla",
                "data_retorno_assinatura",
            ),
            "title": _("Relatório de parcerias"),
        }
        return WeasyTemplateResponse(
            filename="relatorio_convenios.pdf",
            request=request,
            template="convenios/convenios_report.html",
            context=context,
            content_type="application/pdf",
        )

    report_convenios.title = _("Relatório de convênios")

    def get_actions(self, request):
        actions = super(ConvenioAdmin, self).get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions


@admin.register(EquipamentoPrevisto)
class EquipamentoPrevistoAdmin(admin.ModelAdmin):
    list_display = ("convenio", "equipamento", "quantidade")
    list_display_links = ("convenio", "equipamento")
    ordering = ("convenio", "equipamento")
    autocomplete_fields = ("convenio", "equipamento")
    search_fields = (
        "convenio__id",
        "equipamento__fabricante__nome",
        "equipamento__modelo__modelo",
        "equipamento__modelo__tipo__tipo",
    )


@admin.register(Gescon)
class GesconAdmin(admin.ModelAdmin):
    list_display = (
        "url_gescon",
        "email",
    )
    exclude = ["ultima_importacao", "checksums"]


admin.site.register(StatusConvenio)
admin.site.register(TipoSolicitacao)
