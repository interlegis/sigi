from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_weasyprint.views import WeasyTemplateResponse
from import_export.fields import Field
from sigi.apps.casas.forms import OrgaoForm
from sigi.apps.casas.models import Orgao, Funcionario, TipoOrgao
from sigi.apps.casas.filters import (
    GerentesInterlegisFilter,
    ConvenioFilter,
    ExcluirConvenioFilter,
    ServicoFilter,
)
from sigi.apps.contatos.models import Telefone
from sigi.apps.convenios.models import Convenio
from sigi.apps.ocorrencias.models import Ocorrencia
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.servicos.models import Servico
from sigi.apps.servicos.filters import ServicoAtivoFilter
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils import queryset_ascii
from sigi.apps.utils.mixins import CartExportReportMixin, LabeledResourse


class OrgaoExportResourse(LabeledResourse):
    presidente = Field(column_name="presidente")
    telefone = Field(column_name="telefone")
    # servicos_seit = Field(column_name='servicos_seit')
    contato = Field(column_name="contato")

    class Meta:
        model = Orgao
        fields = (
            "municipio__codigo_ibge",
            "cnpj",
            "municipio__codigo_tse",
            "nome",
            "municipio__nome",
            "municipio__uf__sigla",
            "presidente",
            "logradouro",
            "bairro",
            "cep",
            "telefone",
            "pagina_web",
            "email",
            "ult_alt_endereco",
            "contato",
        )
        export_order = fields

    def dehydrate_presidente(self, orgao):
        return orgao.presidente

    def dehydrate_telefone(self, orgao):
        return orgao.telefone

    # def dehydrate_servicos_seit(self, orgao):
    #     servicos = [s.tipo_servico.nome for s in orgao.servico_set.filter(
    #         data_desativacao__isnull=True)]
    #     return ", ".join(servicos)

    def dehydrate_contato(self, orgao):
        return ", ".join(
            [
                f"{c.cargo if c.cargo else 'Sem cargo'}: {c.nome} ({c.email})"
                for c in orgao.funcionario_set.filter(desativado=False)
            ]
        )


class TelefonesInline(GenericTabularInline):
    model = Telefone
    readonly_fields = ("ult_alteracao",)
    extra = 1


class ParlamentarInline(admin.StackedInline):
    model = Parlamentar
    fields = (
        "foto",
        "nome_parlamentar",
        "nome_completo",
        "partido",
        "presidente",
        "data_nascimento",
        "cpf",
        "identidade",
        "telefones",
        "email",
        "redes_sociais",
        "ult_alteracao",
    )
    readonly_fields = ("ult_alteracao",)
    extra = 0

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_delete_permission(self, request, *args, **kwargs):
        return False


class FuncionariosInline(admin.StackedInline):
    model = Funcionario
    fields = (
        "nome",
        "sexo",
        "data_nascimento",
        "nota",
        "email",
        "cargo",
        "funcao",
        "setor",
        "tempo_de_servico",
        "ult_alteracao",
        "endereco",
        "municipio",
        "bairro",
        "cep",
        "redes_sociais",
        "desativado",
        "observacoes",
    )
    autocomplete_fields = ("municipio",)
    readonly_fields = ("ult_alteracao",)
    extra = 1
    verbose_name_plural = _("Contatos da Casa")

    def get_queryset(self, request):
        return (
            self.model.objects.exclude(desativado=True)
            .extra(select={"ult_null": "ult_alteracao is null"})
            .order_by("ult_null", "-ult_alteracao")
            # A função extra foi usada para quando existir um registro com
            # o campo igual a null não aparecer na frente dos mais novos
        )


class ConveniosInline(admin.StackedInline):
    model = Convenio
    fields = (
        "num_processo_sf",
        "link_sigad",
        "status_convenio",
        "num_convenio",
        "projeto",
        "observacao",
        "data_retorno_assinatura",
        "data_termino_vigencia",
        "data_pub_diario",
        "data_sigad",
        "data_solicitacao",
        "get_anexos",
    )
    readonly_fields = [
        "link_sigad",
        "status_convenio",
        "get_anexos",
    ]
    ordering = ("-data_retorno_assinatura",)
    extra = 0
    can_delete = False
    show_change_link = True

    @admin.display(description=_("Anexos"))
    def get_anexos(self, obj):
        return mark_safe(
            render_to_string(
                "admin/casas/anexo_convenio_snippet.html",
                context={"anexos": obj.anexo_set.all()},
            )
        )

    @admin.display(description=_("Status do convênio"))
    def status_convenio(self, obj):
        if obj.pk is None:
            return ""
        status = obj.get_status()
        if status in ["Vencido", "Desistência", "Cancelado"]:
            label = r"danger"
        elif status == "Vigente":
            label = r"success"
        elif status == "Pendente":
            label = r"warning"
        else:
            label = r"info"
        return mark_safe(f'<p class="label label-{label}">{status}</p>')

    @admin.display(description=_("Ver no SIGAD"))
    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return mark_safe(obj.get_sigad_url(display_type="icone"))


class ServicoInline(admin.StackedInline):
    model = Servico
    fields = (
        "tipo_servico",
        "url",
        "hospedagem_interlegis",
        "data_ativacao",
        "data_alteracao",
        "data_desativacao",
        "motivo_desativacao",
    )
    readonly_fields = ["data_alteracao"]
    ordering = ("tipo_servico", "-data_alteracao")
    extra = 0
    show_change_link = True


class OcorrenciaInline(admin.StackedInline):
    model = Ocorrencia
    fields = (
        "data_criacao",
        "categoria",
        "tipo_contato",
        "assunto",
        "prioridade",
        "status",
        "descricao",
        "resolucao",
        "ticket",
        "data_modificacao",
    )
    readonly_fields = (
        "data_criacao",
        "data_modificacao",
    )
    ordering = ("-data_modificacao",)
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        if Servidor.objects.filter(user=request.user).exists():
            return super().has_add_permission(request, obj)
        return False


@admin.register(Orgao)
class OrgaoAdmin(CartExportReportMixin, admin.ModelAdmin):
    form = OrgaoForm
    resource_class = OrgaoExportResourse
    inlines = (
        TelefonesInline,
        ParlamentarInline,
        FuncionariosInline,
        ConveniosInline,
        ServicoInline,
        OcorrenciaInline,
    )
    list_display = (
        "id",
        "sigla",
        "nome",
        "get_uf",
        "get_gerentes",
        "get_convenios",
        "get_servicos",
    )
    list_display_links = (
        "id",
        "sigla",
        "nome",
    )
    list_filter = (
        "tipo",
        ("gerentes_interlegis", GerentesInterlegisFilter),
        "municipio__uf__nome",
        ConvenioFilter,
        ("servico__data_desativacao", ServicoAtivoFilter),
        ExcluirConvenioFilter,
        ServicoFilter,
        "inclusao_digital",
    )
    ordering = ("municipio__uf__nome", "nome")
    queryset = queryset_ascii
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "tipo",
                    "nome",
                    "sigla",
                    "cnpj",
                    "gerentes_interlegis",
                )
            },
        ),
        (
            _("Endereço"),
            {
                "fields": (
                    "data_instalacao",
                    "logradouro",
                    "bairro",
                    "municipio",
                    "cep",
                    "ult_alt_endereco",
                ),
            },
        ),
        (
            _("Presença na Internet"),
            {
                "fields": (
                    "inclusao_digital",
                    "data_levantamento",
                    "pesquisador",
                    "pagina_web",
                    "email",
                    "obs_pesquisa",
                )
            },
        ),
        (
            _("Outras informações"),
            {
                "fields": (
                    "observacoes",
                    "horario_funcionamento",
                    "foto",
                    "brasao",
                ),
            },
        ),
    )
    autocomplete_fields = ("municipio",)
    readonly_fields = [
        "gerentes_interlegis",
    ]
    search_fields = (
        "search_text",
        "sigla",
        "cnpj",
        "bairro",
        "logradouro",
        "cep",
        "municipio__nome",
        "municipio__uf__nome",
        "municipio__codigo_ibge",
        "pagina_web",
        "observacoes",
    )
    reports = [
        "casas_sem_processo",
        "relatorio_simples",
        "relatorio_completo",
        "etiqueta_presidente_25",
        "etiqueta_presidente_39",
        "etiqueta_25",
        "etiqueta_39",
        "etiqueta_parlamentar_25",
        "etiqueta_parlamentar_39",
    ]

    def get_queryset(self, request):
        queryset = super(OrgaoAdmin, self).get_queryset(request)
        return queryset.prefetch_related("gerentes_interlegis", "convenio_set")

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            if formset.model == Ocorrencia:
                formset.save(commit=False)
                for obj in formset.new_objects:
                    if (
                        not hasattr(obj, "servidor_registro")
                        or obj.servidor_registro is None
                    ):
                        obj.servidor_registro = Servidor.objects.get(
                            user=request.user
                        )
        return super().save_related(request, form, formsets, change)

    def get_uf(self, obj):
        return obj.municipio.uf.nome

    get_uf.short_description = _("Unidade da Federação")
    get_uf.admin_order_field = "municipio__uf__nome"

    def get_gerentes(self, obj):
        return mark_safe(obj.lista_gerentes())

    get_gerentes.short_description = _("Gerente Interlegis")

    def get_convenios(self, obj):
        return mark_safe(
            "<ul>"
            + "".join([f"<li>{c}</li>" for c in obj.convenio_set.all()])
            + "</ul>"
        )

    get_convenios.short_description = _("Convênios")

    def get_servicos(self, obj):
        return mark_safe(
            "<ul>"
            + "".join(
                [
                    f'<li><a href="{s.url}" target="_blank">{s}</a></li>'
                    for s in obj.servico_set.filter(
                        data_desativacao__isnull=True
                    )
                ]
            )
            + "</ul>"
        )

    get_servicos.short_description = _("Serviços")

    def lookup_allowed(self, lookup, value):
        return super(OrgaoAdmin, self).lookup_allowed(
            lookup, value
        ) or lookup in [
            "tipo__legislativo__exact",
            "tipo__sigla__exact",
            "municipio__uf__codigo_ibge__exact",
            "convenio__projeto__id__exact",
        ]

    def casas_sem_processo(self, request):
        context = {
            "casas": self.get_queryset(request)
            .filter(convenio=None)
            .order_by("municipio__uf", "nome"),
            "title": _("Casas sem nenhum processo de convênio"),
        }
        return WeasyTemplateResponse(
            filename="casas_sem_processo.pdf",
            request=request,
            template="casas/casas_sem_convenio_pdf.html",
            context=context,
            content_type="application/pdf",
        )

    casas_sem_processo.title = _("Casas sem nenhum processo de convênio")

    def relatorio_simples(self, request):
        context = {
            "casas": self.get_queryset(request).order_by(
                "municipio__uf", "nome"
            ),
            "title": _("Relatório Simples"),
        }
        return WeasyTemplateResponse(
            filename="relatorio_simples.pdf",
            request=request,
            template="casas/casas_sem_convenio_pdf.html",
            context=context,
            content_type="application/pdf",
        )

    relatorio_simples.title = _("Relatório Simples")

    def relatorio_completo(self, request):
        context = {
            "casas": self.get_queryset(request).order_by(
                "municipio__uf", "nome"
            ),
            "title": _("Relatório completo"),
        }
        return WeasyTemplateResponse(
            filename="relatorio_completo.pdf",
            request=request,
            template="casas/relatorio_completo_pdf.html",
            context=context,
            content_type="application/pdf",
        )

    relatorio_completo.title = _("Relatório completo")

    def get_actions(self, request):
        actions = super(OrgaoAdmin, self).get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions


admin.site.register(TipoOrgao)
