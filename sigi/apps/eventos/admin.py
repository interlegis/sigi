import datetime
import time
from typing import Any
from moodle import Moodle
from django.db.models import Q
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template import Template, Context
from django.urls import path, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_weasyprint.utils import django_url_fetcher
from django_weasyprint.views import WeasyTemplateResponse
from import_export.fields import Field
from tinymce.models import HTMLField
from tinymce.widgets import AdminTinyMCE
from weasyprint import HTML
from sigi.apps.eventos.models import (
    Checklist,
    Cronograma,
    ModeloDeclaracao,
    Modulo,
    TipoEvento,
    Solicitacao,
    ItemSolicitado,
    Funcao,
    Evento,
    Equipe,
    Convite,
    Anexo,
)
from sigi.apps.eventos.forms import EventoAdminForm, SelecionaModeloForm
from sigi.apps.utils import abreviatura
from sigi.apps.utils.filters import EmptyFilter, DateRangeFilter
from sigi.apps.utils.mixins import (
    CartExportMixin,
    LabeledResourse,
    ValueLabeledResource,
)


class SolicitacaoStatusFilter(admin.SimpleListFilter):
    title = _("status")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("aberto", _("Aberto")),
            ("analise", _("Análise")),
            ("inconcluso", _("Inconcluso (aberto + análise)")),
            ("concluido", _("Concluído")),
        )

    def queryset(self, request, queryset):
        if self.value() == "aberto":
            return queryset.exclude(
                itemsolicitado__status__in=[
                    ItemSolicitado.STATUS_AUTORIZADO,
                    ItemSolicitado.STATUS_REJEITADO,
                ]
            ).distinct()
        elif self.value() == "analise":
            return (
                queryset.filter(
                    itemsolicitado__status=ItemSolicitado.STATUS_SOLICITADO
                )
                .filter(
                    itemsolicitado__status__in=[
                        ItemSolicitado.STATUS_AUTORIZADO,
                        ItemSolicitado.STATUS_REJEITADO,
                    ]
                )
                .distinct()
            )
        elif self.value() == "inconcluso":
            return queryset.exclude(
                id__in=Solicitacao.objects.exclude(
                    itemsolicitado__status=ItemSolicitado.STATUS_SOLICITADO
                ).only("id")
            )
        elif self.value() == "concluido":
            return queryset.exclude(
                itemsolicitado__status=ItemSolicitado.STATUS_SOLICITADO
            ).distinct()
        return queryset


class SolicitacaoResource(LabeledResourse):
    status = Field(column_name="status")
    oficinas = Field(column_name="oficinas solicitadas")
    oficinas_uf = Field(column_name="número de oficinas realizadas na UF")

    class Meta:
        model = Solicitacao
        fields = (
            "num_processo",
            "status",
            "senador",
            "data_pedido",
            "data_recebido_coperi",
            "oficinas",
            "casa__nome",
            "casa__municipio__nome",
            "casa__municipio__uf__nome",
            "casa__municipio__uf__regiao",
            "casa__municipio__populacao",
            "oficinas_uf",
            "estimativa_casas",
            "estimativa_servidores",
        )
        export_order = fields

    def dehydrate_status(self, obj):
        return obj.get_status()

    def dehydrate_oficinas(self, obj):
        return ", ".join(
            [i.tipo_evento.sigla for i in obj.itemsolicitado_set.all()]
        )

    def dehydrate_oficinas_uf(sekf, obj):
        return Evento.objects.filter(
            status__in=[Evento.STATUS_CONFIRMADO, Evento.STATUS_REALIZADO],
            casa_anfitria__municipio__uf=obj.casa.municipio.uf,
            data_inicio__year__gte=timezone.localdate().year - 2,
        ).count()

    def dehydrate_casa__municipio__uf__regiao(self, obj):
        return obj.casa.municipio.uf.get_regiao_display()


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
        return dict(TipoEvento.CATEGORIA_CHOICES)[
            obj["tipo_evento__categoria"]
        ]

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


class ItemSolicitadoInline(admin.StackedInline):
    model = ItemSolicitado
    fields = (
        "tipo_evento",
        "virtual",
        "inicio_desejado",
        "status",
        "justificativa",
        "servidor",
        "data_analise",
        "evento",
    )
    readonly_fields = ("servidor", "data_analise", "evento")
    extra = 1
    autocomplete_fields = ("tipo_evento",)


@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ["nome", "categoria"]
    list_filter = ["categoria", "casa_solicita"]
    search_fields = ["nome"]
    inlines = [ChecklistInline]


@admin.register(Solicitacao)
class SolicitacaoAdmin(CartExportMixin, admin.ModelAdmin):
    resource_class = SolicitacaoResource
    list_display = (
        "casa",
        "get_sigad_url",
        "get_status",
        "senador",
        "data_pedido",
        "data_recebido_coperi",
        "get_oficinas",
        "get_municipio",
        "get_uf",
        "get_regiao",
        "get_populacao",
        "get_oficinas_uf",
        "estimativa_casas",
        "estimativa_servidores",
    )
    list_filter = (
        "casa__municipio__uf",
        "casa__municipio__uf__regiao",
        "senador",
        "itemsolicitado__tipo_evento",
        SolicitacaoStatusFilter,
    )
    list_select_related = ["casa", "casa__municipio", "casa__municipio__uf"]
    list_display_links = ("casa",)
    search_fields = (
        "casa__search_text",
        "casa__municipio__search_text",
        "casa__municipio__uf__search_text",
        "senador",
    )
    date_hierarchy = "data_pedido"
    inlines = (ItemSolicitadoInline,)
    autocomplete_fields = ("casa",)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        if hasattr(request.user, "servidor"):
            servidor = request.user.servidor
        else:
            servidor = None

        agora = timezone.localtime()

        for item in instances:
            if (
                item.status == ItemSolicitado.STATUS_SOLICITADO
                and item.evento is not None
            ):
                item.evento.status = Evento.STATUS_ACONFIRMAR
                self.message_user(
                    request,
                    _(
                        f"Status do evento {item.evento} alterado para "
                        f"{item.evento.get_status_display()}"
                    ),
                    messages.INFO,
                )
            elif item.status == ItemSolicitado.STATUS_AUTORIZADO:
                item.servidor = servidor
                item.data_analise = agora
                if item.evento is None:
                    item.evento = Evento(
                        tipo_evento=item.tipo_evento,
                        nome=_(
                            f"{item.tipo_evento} em {item.solicitacao.casa}"[
                                :100
                            ]
                        ),
                        descricao=_(
                            f"{item.tipo_evento} em {item.solicitacao.casa}"
                        ),
                        virtual=item.virtual,
                        solicitante=item.solicitacao.senador,
                        num_processo=item.solicitacao.num_processo,
                        data_pedido=item.solicitacao.data_pedido,
                        data_recebido_coperi=item.solicitacao.data_recebido_coperi,
                        data_inicio=item.inicio_desejado,
                        data_termino=item.inicio_desejado
                        + datetime.timedelta(days=item.tipo_evento.duracao),
                        casa_anfitria=item.solicitacao.casa,
                        observacao=_(
                            f"Autorizado por {servidor} com a justificativa '{item.justificativa}"
                        ),
                        status=Evento.STATUS_CONFIRMADO,
                        contato=item.solicitacao.contato,
                        telefone=item.solicitacao.telefone_contato,
                    )
                    self.message_user(
                        request,
                        _(f"Evento {item.evento} criado automaticamente."),
                        messages.INFO,
                    )
                else:
                    item.evento.status = Evento.STATUS_CONFIRMADO
                    item.evento.observacao += _(
                        f"\nConfirmado por {servidor} com a justificativa: {item.justificativa}"
                    )
                    item.evento.data_cancelamento = None
                    item.evento.motivo_cancelamento = ""
                    self.message_user(
                        request,
                        _(
                            f"Status do evento {item.evento} alterado para "
                            f"{item.evento.get_status_display()}"
                        ),
                        messages.INFO,
                    )
            elif item.status == ItemSolicitado.STATUS_REJEITADO:
                item.servidor = servidor
                item.data_analise = agora
                if item.evento is not None:
                    item.evento.status = Evento.STATUS_CANCELADO
                    item.evento.observacao += _(
                        f"\nCancelado por {servidor} com a justificativa: {item.justificativa}"
                    )
                    item.evento.data_cancelamento = timezone.localdate()
                    item.evento.motivo_cancelamento = _(
                        f"\nCancelado por {servidor} com a justificativa: {item.justificativa}"
                    )
                    self.message_user(
                        request,
                        _(
                            f"Status do evento {item.evento} alterado para "
                            f"{item.evento.get_status_display()}"
                        ),
                        messages.INFO,
                    )
            if item.evento:
                item.evento.tipo_evento = item.tipo_evento
                item.evento.nome = _(
                    f"{item.tipo_evento} em {item.solicitacao.casa}"[:100]
                )
                item.evento.descricao = _(
                    f"{item.tipo_evento} em {item.solicitacao.casa}"
                )
                item.evento.virtual = item.virtual
                item.evento.solicitante = item.solicitacao.senador
                item.evento.num_processo = item.solicitacao.num_processo
                item.evento.data_pedido = item.solicitacao.data_pedido
                item.evento.data_recebido_coperi = (
                    item.solicitacao.data_recebido_coperi
                )
                item.evento.data_inicio = item.inicio_desejado
                item.evento.data_termino = (
                    item.inicio_desejado
                    + datetime.timedelta(days=item.tipo_evento.duracao)
                )
                item.evento.casa_anfitria = item.solicitacao.casa
                item.evento.contato = item.solicitacao.contato
                item.evento.telefone = item.solicitacao.telefone_contato
                item.evento.save()
            item.save()
        return super().save_formset(request, form, formset, change)

    @admin.display(description=_("Oficinas solicitadas"))
    def get_oficinas(self, obj):
        return mark_safe(
            "<ul><li>"
            + "</li><li>".join(
                [i.tipo_evento.sigla for i in obj.itemsolicitado_set.all()]
            )
            + "</li></ul>"
        )

    @admin.display(
        description=_("Município"), ordering="casa__municipio__nome"
    )
    def get_municipio(self, obj):
        return obj.casa.municipio.nome

    @admin.display(description=_("UF"), ordering="casa__municipio__uf__nome")
    def get_uf(self, obj):
        return obj.casa.municipio.uf.nome

    @admin.display(
        description=_("Região"), ordering="casa__municipio__uf__regiao"
    )
    def get_regiao(self, obj):
        return obj.casa.municipio.uf.get_regiao_display()

    @admin.display(
        description=_("População"), ordering="casa__municipio__populacao"
    )
    def get_populacao(self, obj):
        return obj.casa.municipio.populacao


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
        "get_tipo_evento",
        "nome",
        "turma",
        "status",
        "publicar",
        "link_sigad",
        "data_inicio",
        "data_termino",
        "get_municipio",
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
        "solicitante",
    )
    autocomplete_fields = (
        "tipo_evento",
        "casa_anfitria",
    )
    search_fields = (
        "nome",
        "tipo_evento__nome",
        "casa_anfitria__search_text",
        "casa_anfitria__municipio__search_text",
        "solicitante",
        "num_processo",
    )
    inlines = (
        EquipeInline,
        ConviteInline,
        ModuloInline,
        AnexoInline,
        CronogramaInline,
    )
    save_as = True

    @admin.display(description=_("Tipo Evento"), ordering="tipo_evento__nome")
    def get_tipo_evento(self, obj):
        return obj.tipo_evento.nome

    @admin.display(
        description=_("Município"), ordering="casa_anfitria__municipio"
    )
    def get_municipio(self, obj):
        if obj.casa_anfitria:
            return str(obj.casa_anfitria.municipio)
        else:
            return None

    @admin.display(
        description=_("número do processo SIGAD"), ordering="num_processo"
    )
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

    def render_change_form(self, request, context, add, change, form_url, obj):
        perm = request.user.has_perm("eventos.createcourse_evento")
        context.update(
            {
                "can_createcourse": (
                    perm
                    and obj
                    and obj.moodle_courseid is None
                    and obj.tipo_evento.moodle_template_courseid is not None
                    and obj.tipo_evento.moodle_categoryid is not None
                ),
                "can_updateparticipantes": (
                    perm and obj and obj.moodle_courseid is not None
                ),
            }
        )
        return super().render_change_form(
            request, context, add, change, form_url, obj
        )

    def lookup_allowed(self, lookup, value):
        return super(EventoAdmin, self).lookup_allowed(
            lookup, value
        ) or lookup in [
            "tipo_evento__nome__exact",
            "tipo_evento__nome__contains",
        ]

    def get_urls(self):
        urls = super().get_urls()
        model_info = self.get_model_info()
        my_urls = [
            path(
                "<path:object_id>/declaracao/",
                self.admin_site.admin_view(self.declaracao_report),
                name="%s_%s_declaracaoreport" % model_info,
            ),
            path(
                "<path:object_id>/gant/",
                self.admin_site.admin_view(self.gant_report),
                name="%s_%s_gantreport" % model_info,
            ),
            path(
                "<path:object_id>/checklist/",
                self.admin_site.admin_view(self.checklist_report),
                name="%s_%s_checklistreport" % model_info,
            ),
            path(
                "<path:object_id>/comunicacao/",
                self.admin_site.admin_view(self.plano_comunicacao),
                name="%s_%s_comunicacaoreport" % model_info,
            ),
            path(
                "<path:object_id>/createcourse/",
                self.admin_site.admin_view(self.create_course),
                name="%s_%s_createcourse" % model_info,
            ),
            path(
                "<path:object_id>/updateparticipantes/",
                self.admin_site.admin_view(self.update_participantes),
                name="%s_%s_updateparticipantes" % model_info,
            ),
        ]
        return my_urls + urls

    def declaracao_report(self, request, object_id):
        if request.method == "POST":
            form = SelecionaModeloForm(request.POST)
            if form.is_valid():
                evento = get_object_or_404(Evento, id=object_id)
                modelo = form.cleaned_data["modelo"]
                membro = (
                    evento.equipe_set.filter(assina_oficio=True).first()
                    or evento.equipe_set.first()
                )
                if membro:
                    servidor = membro.membro
                else:
                    servidor = None
                template_string = (
                    """
                    {% extends "eventos/declaracao_pdf.html" %}
                    {% block text_body %}"""
                    + modelo.texto
                    + """
                    {% endblock %}
                    """
                )
                context = Context(
                    {
                        "pagesize": modelo.formato,
                        "pagemargin": modelo.margem,
                        "evento": evento,
                        "servidor": servidor,
                        "data": evento.data_inicio.date(),
                    }
                )
                string = Template(template_string).render(context)
                # return HttpResponse(string)
                response = HttpResponse(
                    headers={
                        "Content-Type": "application/pdf",
                        "Content-Disposition": 'attachment; filename="declaração.pdf"',
                    }
                )
                pdf = HTML(
                    string=string,
                    url_fetcher=django_url_fetcher,
                    encoding="utf-8",
                    base_url=request.build_absolute_uri("/"),
                )
                pdf.write_pdf(target=response)
                return response
        else:
            form = SelecionaModeloForm()

        context = {
            "form": form,
            "evento_id": object_id,
            "opts": self.model._meta,
            "preserved_filters": self.get_preserved_filters(request),
        }
        return render(
            request, "admin/eventos/evento/seleciona_modelo.html", context
        )

    def gant_report(self, request, object_id):
        evento = get_object_or_404(Evento, id=object_id)
        change_url = (
            reverse(
                "admin:%s_%s_change" % self.get_model_info(), args=[object_id]
            )
            + "?"
            + self.get_preserved_filters(request)
        )
        cronograma = list(
            evento.cronograma_set.order_by("data_prevista_inicio")
        )
        if not cronograma:
            self.message_user(
                request,
                _(
                    "Não há um cronograma definido para a realização deste evento. Impossível gerar um gráfico de Gant"
                ),
                messages.ERROR,
            )
            return redirect(change_url)

        inicio = min(
            cronograma[0].data_prevista_inicio,
            cronograma[0].data_inicio or cronograma[0].data_prevista_inicio,
        )
        termino = max(
            cronograma[-1].data_prevista_termino,
            cronograma[-1].data_termino
            or cronograma[-1].data_prevista_termino,
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
        change_url = (
            reverse(
                "admin:%s_%s_change" % self.get_model_info(), args=[object_id]
            )
            + "?"
            + self.get_preserved_filters(request)
        )
        cronograma = list(
            evento.cronograma_set.order_by("data_prevista_inicio")
        )
        if not cronograma:
            self.message_user(
                request,
                _(
                    "Não há um cronograma definido para a realização deste evento. Impossível gerar um checklist"
                ),
                messages.ERROR,
            )
            return redirect(change_url)

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
        change_url = (
            reverse(
                "admin:%s_%s_change" % self.get_model_info(), args=[object_id]
            )
            + "?"
            + self.get_preserved_filters(request)
        )
        cronograma = list(
            evento.cronograma_set.order_by("data_prevista_inicio")
        )
        if not cronograma:
            self.message_user(
                request,
                _(
                    "Não há um cronograma definido para a realização deste evento. Impossível gerar um plano de comunicação"
                ),
                messages.ERROR,
            )
            return redirect(change_url)

        matrix = {}
        for etapa in cronograma:
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

    def create_course(self, request, object_id):
        evento = get_object_or_404(Evento, id=object_id)
        change_url = (
            reverse(
                "admin:%s_%s_change" % self.get_model_info(), args=[object_id]
            )
            + "?"
            + self.get_preserved_filters(request)
        )
        if evento.moodle_courseid is not None:
            self.message_user(
                request,
                _("Este evento já tem curso associado no Saberes"),
                level=messages.ERROR,
            )
            return redirect(change_url)
        if (
            evento.tipo_evento.moodle_template_courseid is None
            or evento.tipo_evento.moodle_categoryid is None
        ):
            self.message_user(
                request,
                _("Este tipo de evento não possui template no Saberes"),
                level=messages.ERROR,
            )
            return redirect(change_url)
        if evento.data_inicio is None or evento.data_termino is None:
            self.message_user(
                request,
                _(
                    "O evento precisa ter datas de início e término para criar "
                    "curso no Saberes."
                ),
                level=messages.ERROR,
            )
            return redirect(change_url)

        if evento.turma == "":
            self.message_user(
                request,
                _(
                    "Preencha (e salve!) o campo Turma para poder criar o "
                    "curso no Saberes"
                ),
                level=messages.ERROR,
            )
            return redirect(change_url)

        api_url = f"{settings.MOODLE_BASE_URL}/webservice/rest/server.php"
        mws = Moodle(api_url, settings.MOODLE_API_TOKEN)
        fullname = f"{evento.tipo_evento.nome} - {evento.casa_anfitria.municipio.nome}/{evento.casa_anfitria.municipio.uf.sigla} - {evento.tipo_evento.prefixo_turma}{evento.turma}"
        shortname = f"{abreviatura(evento.tipo_evento.nome)} - {evento.tipo_evento.prefixo_turma}{evento.turma}"
        inicio = int(time.mktime(evento.data_inicio.astimezone().timetuple()))
        fim = int(time.mktime(evento.data_termino.astimezone().timetuple()))
        erros = []
        try:  # Criar novo curso a partir do template
            novo_curso = mws.core.course.duplicate_course(
                evento.tipo_evento.moodle_template_courseid,
                fullname=fullname,
                shortname=shortname,
                categoryid=evento.tipo_evento.moodle_categoryid,
                visible=0,
            )
            evento.moodle_courseid = novo_curso.id
            evento.save()
        except Exception as e:
            self.message_user(
                request,
                _(
                    "Ocorreu um erro ao criar o curso no Saberes com "
                    f"a mensagem {e.message}"
                ),
                level=messages.ERROR,
            )
            return redirect(change_url)
        try:  # Atualiza configuração do curso
            changes = {
                "id": novo_curso.id,
                "summary": evento.descricao,
                "startdate": inicio,
                "enddate": fim,
            }
            res = mws.core.course.update_courses([changes])
        except Exception as e:
            erros.append(
                _(
                    "Falha na tentativa de alterar o sumário e as datas de "
                    "início e término do curso, com a seguinte mensagem: "
                    f"{e.message}"
                )
            )
        try:  # Matricular professores/membros
            membros = evento.equipe_set.exclude(
                membro__moodle_userid=None
            ).exclude(funcao__moodle_roleid=None)
            equipe = []
            for membro in membros:
                equipe.append(
                    {
                        "roleid": membro.funcao.moodle_roleid,
                        "userid": membro.membro.moodle_userid,
                        "courseid": evento.moodle_courseid,
                    }
                )
            mws.enrol.manual.enrol_users(equipe)
        except Exception as e:
            erros.append(
                _(
                    "Falha ao tentar inscrever a equipe no curso do Saberes, "
                    f"com a seguinte mensagem: {e.message}"
                )
            )
        context = {
            "evento": evento,
            "fullname": fullname,
            "shortname": shortname,
            "membros": membros,
            "erros": erros,
            "opts": self.model._meta,
            "preserved_filters": self.get_preserved_filters(request),
        }
        return render(
            request, "admin/eventos/evento/createcourse.html", context
        )

    def update_participantes(self, request, object_id):
        evento = get_object_or_404(Evento, id=object_id)
        change_url = (
            reverse(
                "admin:%s_%s_change" % self.get_model_info(), args=[object_id]
            )
            + "?"
            + self.get_preserved_filters(request)
        )
        if evento.moodle_courseid is None:
            self.message_user(
                request,
                _("Este evento não tem curso associado no Saberes"),
                level=messages.ERROR,
            )
            return redirect(change_url)

        api_url = f"{settings.MOODLE_BASE_URL}/webservice/rest/server.php"
        mws = Moodle(api_url, settings.MOODLE_API_TOKEN)
        try:
            inscritos = mws.post(
                "core_enrol_get_enrolled_users",
                courseid=evento.moodle_courseid,
            )
        except Exception as e:
            self.message_user(
                request,
                _(
                    "Ocorreu um erro ao acessar o curso no Saberes com "
                    f"a mensagem {e.message}"
                ),
                level=messages.ERROR,
            )
            return redirect(change_url)
        evento.total_participantes = len(
            list(
                filter(
                    lambda u: any(
                        r["roleid"] in settings.MOODLE_STUDENT_ROLES
                        for r in u["roles"]
                    ),
                    inscritos,
                )
            )
        )
        evento.save()
        self.message_user(
            request,
            _(
                f"Foram encontrados {evento.total_participantes} alunos "
                "no Saberes"
            ),
            level=messages.SUCCESS,
        )
        return redirect(change_url)
