import datetime
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_weasyprint.views import WeasyTemplateResponse
from import_export.fields import Field
from tinymce.models import HTMLField
from tinymce.widgets import AdminTinyMCE
from sigi.apps.eventos.models import (
    Checklist,
    Cronograma,
    ModeloDeclaracao,
    Modulo,
    TipoEvento,
    Funcao,
    Evento,
    Equipe,
    Convite,
    Anexo,
)
from sigi.apps.eventos.forms import EventoAdminForm
from sigi.apps.utils.filters import EmptyFilter, DateRangeFilter
from sigi.apps.utils.mixins import CartExportMixin, ValueLabeledResource


class EventoResource(ValueLabeledResource):
    # categoria_evento = Field(column_name="tipo_evento__categoria")
    # status = Field(column_name="status")
    class Meta:
        model = Evento
        fields = (
            "id",
            "tipo_evento__nome",
            "tipo_evento__categoria",
            "nome",
            "descricao",
            "virtual",
            "solicitante",
            "num_processo",
            "data_pedido",
            "data_inicio",
            "data_termino",
            "carga_horaria",
            "casa_anfitria__nome",
            "casa_anfitria__logradouro",
            "casa_anfitria__bairro",
            "casa_anfitria__municipio__nome",
            "casa_anfitria__municipio__uf__sigla",
            "casa_anfitria__cep",
            "casa_anfitria__email",
            "local",
            "municipio__nome",
            "municipio__uf__sigla",
            "observacao",
            "publico_alvo",
            "total_participantes",
            "status",
            "data_cancelamento",
            "motivo_cancelamento",
            "equipe__membro__nome_completo",
            "equipe__funcao__nome",
            "convite__casa__nome",
            "convite__casa__municipio__nome",
            "convite__casa__municipio__uf__sigla",
            "convite__casa__cep",
            "convite__casa__email",
            "convite__qtde_participantes",
            "convite__nomes_participantes",
        )
        export_order = fields

    def dehydrate_tipo_evento__categoria(self, obj):
        return dict(TipoEvento.CATEGORIA_CHOICES)[obj["tipo_evento__categoria"]]

    def dehydrate_virtual(self, obj):
        return "Sim" if obj["virtual"] else "Não"

    def dehydrate_status(self, obj):
        return dict(Evento.STATUS_CHOICES)[obj["status"]]


class ChecklistInline(admin.StackedInline):
    model = Checklist


class EquipeInline(admin.StackedInline):
    model = Equipe
    autocomplete_fields = ("membro", "funcao")


class ConviteInline(admin.StackedInline):
    model = Convite
    autocomplete_fields = ("casa",)


class ModuloInline(admin.StackedInline):
    model = Modulo
    autocomplete_fields = ("apresentador", "monitor")


class AnexoInline(admin.StackedInline):
    model = Anexo
    exclude = ("data_pub", "convite")


class CronogramaInline(admin.StackedInline):
    model = Cronograma
    extra = 0


@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ["nome", "categoria"]
    list_filter = ["categoria", "casa_solicita"]
    search_fields = ["nome"]
    inlines = [ChecklistInline]


@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "descricao",
    )
    search_fields = (
        "nome",
        "descricao",
    )


@admin.register(ModeloDeclaracao)
class ModeloDeclaracaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "formato")
    formfield_overrides = {HTMLField: {"widget": AdminTinyMCE}}


@admin.register(Evento)
class EventoAdmin(CartExportMixin, admin.ModelAdmin):
    form = EventoAdminForm
    resource_class = EventoResource
    date_hierarchy = "data_inicio"
    list_display = (
        "get_banner",
        "nome",
        "tipo_evento",
        "turma",
        "status",
        "publicar",
        "link_sigad",
        "data_inicio",
        "data_termino",
        "municipio",
        "solicitante",
        "total_participantes",
    )
    list_display_links = ("get_banner", "nome")
    list_filter = (
        "status",
        "publicar",
        ("num_processo", EmptyFilter),
        "tipo_evento",
        "tipo_evento__categoria",
        ("data_inicio", DateRangeFilter),
        "virtual",
        "municipio__uf",
        "solicitante",
    )
    autocomplete_fields = (
        "tipo_evento",
        "solicitacao",
        "casa_anfitria",
        "municipio",
    )
    search_fields = (
        "nome",
        "tipo_evento__nome",
        "casa_anfitria__search_text",
        "municipio__search_text",
        "solicitante",
    )
    inlines = (
        EquipeInline,
        ConviteInline,
        ModuloInline,
        AnexoInline,
        CronogramaInline,
    )
    save_as = True

    @admin.display(description=_("número do processo SIGAD"))
    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return mark_safe(obj.get_sigad_url())

    @admin.display(description=_("banner"))
    def get_banner(self, obj):
        if obj.banner:
            return mark_safe(
                f'<img src="{obj.banner.url}" width="60" height="60" />'
            )
        else:
            return ""

    def lookup_allowed(self, lookup, value):
        return super(EventoAdmin, self).lookup_allowed(
            lookup, value
        ) or lookup in [
            "tipo_evento__nome__exact",
            "tipo_evento__nome__contains",
        ]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "<path:object_id>/gant/",
                self.admin_site.admin_view(self.gant_report),
                name="%s_%s_gantreport" % self.get_model_info(),
            ),
            path(
                "<path:object_id>/checklist/",
                self.admin_site.admin_view(self.checklist_report),
                name="%s_%s_checklistreport" % self.get_model_info(),
            ),
            path(
                "<path:object_id>/comunicacao/",
                self.admin_site.admin_view(self.plano_comunicacao),
                name="%s_%s_comunicacaoreport" % self.get_model_info(),
            ),
        ]
        return my_urls + urls

    def gant_report(self, request, object_id):
        evento = get_object_or_404(Evento, id=object_id)
        cronograma = list(
            evento.cronograma_set.order_by("data_prevista_inicio")
        )
        inicio = min(
            cronograma[0].data_prevista_inicio,
            cronograma[0].data_inicio or cronograma[0].data_prevista_inicio,
        )
        termino = max(
            cronograma[-1].data_prevista_termino,
            cronograma[-1].data_termino or cronograma[-1].data_prevista_termino,
        )
        datas = [
            inicio + datetime.timedelta(days=x)
            for x in range((termino - inicio).days + 1)
        ]
        context = {
            "cronograma": cronograma,
            "datas": datas,
            "hoje": datetime.date.today(),
            "title": evento.nome,
        }

        return WeasyTemplateResponse(
            filename="grafico-gant.pdf",
            request=request,
            template="admin/eventos/evento/gant_report.html",
            context=context,
            content_type="application/pdf",
        )

    def checklist_report(self, request, object_id):
        evento = get_object_or_404(Evento, id=object_id)
        cronograma = list(
            evento.cronograma_set.order_by("data_prevista_inicio")
        )
        context = {"cronograma": cronograma, "title": evento.nome}
        return WeasyTemplateResponse(
            filename="checklist.pdf",
            request=request,
            template="admin/eventos/evento/checklist_report.html",
            context=context,
            content_type="application/pdf",
        )

    def plano_comunicacao(self, request, object_id):
        evento = get_object_or_404(Evento, id=object_id)
        matrix = {}
        for etapa in evento.cronograma_set.order_by("data_prevista_inicio"):
            for responsavel in etapa.responsaveis.splitlines():
                if responsavel not in matrix:
                    matrix[responsavel] = {}
                for destinatario in etapa.comunicar_inicio.splitlines():
                    if destinatario not in matrix[responsavel]:
                        matrix[responsavel][destinatario] = []
                    matrix[responsavel][destinatario].append(
                        _(f"Início da etapa {etapa.nome}")
                    )
                for destinatario in etapa.comunicar_termino.splitlines():
                    if destinatario not in matrix[responsavel]:
                        matrix[responsavel][destinatario] = []
                    matrix[responsavel][destinatario].append(
                        _(f"Término da etapa {etapa.nome}")
                    )
        responsaveis = list(matrix.keys())
        destinatarios = list(
            {x for xs in [v.keys() for v in matrix.values()] for x in xs}
        )
        responsaveis.sort()
        destinatarios.sort()
        matrix = {
            resp: {
                dest: matrix[resp][dest] if dest in matrix[resp] else []
                for dest in destinatarios
            }
            for resp in responsaveis
        }
        context = {
            "matrix": matrix,
            "destinatarios": destinatarios,
            "title": evento.nome,
        }
        return WeasyTemplateResponse(
            filename="comunicação.pdf",
            request=request,
            template="admin/eventos/evento/plano_comunicacao.html",
            context=context,
            content_type="application/pdf",
        )
