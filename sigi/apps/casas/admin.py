from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_weasyprint.views import WeasyTemplateResponse
from import_export.fields import Field
from sigi.apps.casas.forms import OrgaoForm
from sigi.apps.casas.models import Orgao, Funcionario, TipoOrgao
from sigi.apps.casas.filters import (
    GerentesInterlegisFilter,
    ServicoFilter,
)
from sigi.apps.convenios.filters import (
    TipoProjetoFilter,
    ExcluirTipoProjetoFilter,
)
from sigi.apps.contatos.models import Telefone
from sigi.apps.convenios.models import Convenio
from sigi.apps.ocorrencias.models import Ocorrencia
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.servicos.models import Servico
from sigi.apps.servicos.filters import ServicoAtivoFilter
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils import asciify_q_param
from sigi.apps.utils.filters import EmptyFilter
from sigi.apps.utils.mixins import (
    ReturnMixin,
    CartExportReportMixin,
    LabeledResourse,
)


class OrgaoExportResourceContato(LabeledResourse):
    class Meta:
        model = Orgao
        fields = ("nome", "email")
        export_order = fields
        name = "Exportação para aplicativo Contatos"

    def dehydrate_nome(self, orgao):
        return orgao.nome[:50]

    def export(self, queryset=None, *args, **kwargs):
        if queryset is not None:
            queryset = queryset.exclude(email="")
        return super().export(queryset, *args, **kwargs)


class OrgaoExportResourseGeral(LabeledResourse):
    presidente = Field(column_name="presidente")
    telefone = Field(column_name="telefone")
    # servicos_seit = Field(column_name='servicos_seit')
    contato = Field(column_name="contato")
    nome = Field(column_name="nome")

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
        name = "Exportação de uso geral"

    def dehydrate_nome(self, orgao):
        return orgao.nome[:50]

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


class ParlamentarInline(admin.TabularInline):
    model = Parlamentar
    template = "admin/casas/orgao/tabular.html"
    fields = (
        "get_foto",
        "nome_parlamentar",
        "status_mandato",
        "get_partido",
        "email",
        "redes_sociais",
        "presidente",
    )
    readonly_fields = fields
    extra = 0
    max_num = 0
    show_change_link = True
    can_delete = False

    @mark_safe
    @admin.display(description=_("Foto"))
    def get_foto(self, obj):
        if obj.foto:
            return f'<img class="circle" src="{obj.foto.url}" style="width: 58px; height: 58px;"/>'
        else:
            return (
                '<i class="material-icons medium grey-text">account_circle</i>'
            )

    @admin.display(description=_("Partido"))
    def get_partido(self, obj):
        return obj.partido.sigla


class FuncionarioInline(admin.TabularInline):
    model = Funcionario
    template = "admin/casas/orgao/tabular.html"
    fields = (
        "get_setor",
        "nome",
        "nota",
        "get_email_link",
        "ult_alteracao",
        "observacoes",
    )
    readonly_fields = fields
    extra = 0
    max_num = 0
    show_change_link = True
    can_delete = False
    verbose_name_plural = _("Contatos da Casa")
    ordering = ["setor", "-ult_alteracao"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(desativado=True)

    @admin.display(description=_("setor"))
    def get_setor(self, func):
        if func.setor == "contato_interlegis":
            return format_html(
                "<span class='green lighten-5 z-depth-1'>{setor}</span>",
                setor=func.get_setor_display(),
            )
        return func.get_setor_display()

    @admin.display(description=_("e-mail"))
    def get_email_link(self, func):
        return format_html(
            "<a href='mailto:{email}' targe='_blank'>{email}</a>",
            email=func.email,
        )


class ConveniosInline(admin.TabularInline):
    model = Convenio
    template = "admin/casas/orgao/tabular.html"
    fields = (
        "num_processo_sf",
        "link_sigad",
        "status_convenio",
        "num_convenio",
        "projeto",
        "data_retorno_assinatura",
        "data_termino_vigencia",
        "data_pub_diario",
        "data_sigad",
        "data_solicitacao",
    )
    readonly_fields = fields
    ordering = ("-data_retorno_assinatura",)
    readonly_fields = fields
    extra = 0
    max_num = 0
    show_change_link = True
    can_delete = False

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


class ServicoInline(admin.TabularInline):
    model = Servico
    template = "admin/casas/orgao/tabular.html"
    fields = (
        "get_tipo_servico",
        "get_url",
        "hospedagem_interlegis",
        "data_ativacao",
        "data_desativacao",
        "resultado_verificacao",
        "data_ultimo_uso",
    )
    readonly_fields = fields
    ordering = ("-data_desativacao", "-data_ativacao", "tipo_servico")
    extra = 0
    max_num = 0
    show_change_link = True
    can_delete = False

    @admin.display(description=_("Tipo de serviço"), ordering="tipo_servico")
    def get_tipo_servico(self, obj):
        return obj.tipo_servico.sigla

    @mark_safe
    @admin.display(description="Url do serviço", ordering="url")
    def get_url(self, obj):
        return f"<a href='{obj.url}' target='_blank'>{obj.url}</a>"


class OcorrenciaInline(admin.TabularInline):
    model = Ocorrencia
    template = "admin/casas/orgao/tabular.html"
    fields = (
        "data_criacao",
        "data_modificacao",
        "categoria",
        "tipo_contato",
        "assunto",
        "prioridade",
        "status",
    )
    autocomplete_fields = ("categoria", "tipo_contato")
    readonly_fields = fields
    ordering = ("-data_modificacao",)
    extra = 0
    max_num = 0
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj):
        if Servidor.objects.filter(user=request.user).exists():
            return super().has_add_permission(request, obj)
        return False

    def has_change_permission(self, request, obj):
        if Servidor.objects.filter(user=request.user).exists():
            return super().has_change_permission(request, obj)
        return False


@admin.register(TipoOrgao)
class TipoOrgaoAdmin(admin.ModelAdmin):
    list_display = ("sigla", "nome", "legislativo")
    list_filter = ("legislativo",)
    search_fields = ("sigla", "nome")


@admin.register(Funcionario)
class FuncionarioAdmin(ReturnMixin, admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("nome", "sexo", "data_nascimento")}),
        (_("Documentos"), {"fields": ("cpf", "identidade")}),
        (_("Contato"), {"fields": ("nota", "email", "redes_sociais")}),
        (
            _("Endereço"),
            {"fields": ("endereco", "municipio", "bairro", "cep")},
        ),
        (
            _("Vínculo"),
            {
                "fields": (
                    "casa_legislativa",
                    "cargo",
                    "funcao",
                    "setor",
                    "tempo_de_servico",
                )
            },
        ),
        (
            _("Validade"),
            {"fields": ("ult_alteracao", "desativado", "observacoes")},
        ),
    )
    readonly_fields = ("ult_alteracao",)
    autocomplete_fields = ("casa_legislativa", "municipio")


@admin.register(Orgao)
class OrgaoAdmin(CartExportReportMixin, admin.ModelAdmin):
    form = OrgaoForm
    resource_classes = [OrgaoExportResourseGeral, OrgaoExportResourceContato]
    inlines = (
        TelefonesInline,
        ParlamentarInline,
        FuncionarioInline,
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
        ("convenio__projeto_id", TipoProjetoFilter),
        ("servico__data_desativacao", ServicoAtivoFilter),
        ("convenio__projeto_id", ExcluirTipoProjetoFilter),
        ServicoFilter,
        "inclusao_digital",
        ("email", EmptyFilter),
    )
    ordering = ("municipio__uf__nome", "nome")
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
                    "telefone_geral",
                    "horario_funcionamento",
                    "observacoes",
                    "foto",
                    "brasao",
                ),
            },
        ),
    )
    autocomplete_fields = ("tipo", "municipio", "pesquisador")
    readonly_fields = ["gerentes_interlegis", "ult_alt_endereco"]
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
        asciify_q_param(request)
        queryset = super().get_queryset(request)
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
            + "".join(
                [
                    f"<li>{c}</li>"
                    for c in obj.convenio_set.order_by(
                        "-data_retorno_assinatura"
                    )
                ]
            )
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
