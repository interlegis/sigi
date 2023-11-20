import datetime
import pandas as pd
import time
from moodle import Moodle
from typing import Any
from django.db import models
from django.db.models import (
    F,
    OuterRef,
    Subquery,
    Count,
    Q,
    Sum,
    Avg,
    Min,
    Max,
    Prefetch,
    Case,
    When,
)
from django.db.models.functions import ExtractDay, Cast
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
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
from sigi.apps.convenios.models import Convenio
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.eventos.models import (
    Checklist,
    Cronograma,
    ModeloDeclaracao,
    Modulo,
    TipoEvento,
    Solicitacao,
    AnexoSolicitacao,
    ItemSolicitado,
    Funcao,
    Evento,
    Equipe,
    Convite,
    Anexo,
)
from sigi.apps.eventos.forms import EventoAdminForm, SelecionaModeloForm
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils import abreviatura
from sigi.apps.utils.filters import DateRangeFilter
from sigi.apps.utils.mixins import (
    CartExportMixin,
    CartExportReportMixin,
    LabeledResourse,
    ValueLabeledResource,
)


class ActVigenteFilter(admin.SimpleListFilter):
    title = _("ACT vigente")
    parameter_name = "act_vigente"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(act_id=None)
        if self.value() == "no":
            return queryset.filter(act_id=None)


class NumeroParticipantesFilter(admin.SimpleListFilter):
    title = _("Inscritos x Aprovados")
    parameter_name = "inscritos_x_aprovados"

    def lookups(self, request, model_admin):
        return (
            ("sem_inscritos", _("Sem inscritos")),
            ("sem_aprovados", _("Sem aprovados")),
            ("diferenca_10", _("Diferença >= dez")),
        )

    def queryset(self, request, queryset):
        if self.value() == "sem_inscritos":
            return queryset.filter(inscritos_saberes=0)
        if self.value() == "sem_aprovados":
            return queryset.filter(aprovados_saberes=0)
        if self.value() == "diferenca_10":
            return queryset.annotate(
                diferenca=F("inscritos_saberes") - F("aprovados_saberes")
            ).filter(diferenca__gte=10)


class SolicitacaoResource(LabeledResourse):
    act_vigente = Field(column_name="ACT vigente")
    data_termino_act = Field(column_name="término vigência ACT")
    oficinas = Field(column_name="oficinas solicitadas")
    oficinas_municipio = Field(
        column_name="oficinas atendidas/confirmadas no município"
    )
    oficinas_uf = Field(column_name="oficinas atendidas/confirmadas na UF")
    oficinas_microrregiao = Field(
        column_name="oficinas atendidas/confirmadas na microrregião"
    )

    class Meta:
        model = Solicitacao
        fields = (
            "num_processo",
            "status",
            "senador",
            "act_vigente",
            "data_termino_act",
            "data_pedido",
            "data_recebido_coperi",
            "oficinas",
            "casa__nome",
            "casa__municipio__nome",
            "casa__municipio__populacao",
            "oficinas_municipio",
            "casa__municipio__uf__nome",
            "oficinas_uf",
            "casa__municipio__uf__regiao",
            "casa__municipio__microrregiao__nome",
            "oficinas_microrregiao",
            "estimativa_casas",
            "estimativa_servidores",
        )
        export_order = fields

    def dehydrate_status(self, obj):
        return obj.get_status_display()

    def dehydrate_act_vigente(self, obj):
        return obj.act_num

    def dehydrate_data_termino_act(self, obj):
        return obj.act_data_termino_vigencia

    def dehydrate_oficinas(self, obj):
        return ", ".join(
            [i.tipo_evento.sigla for i in obj.itemsolicitado_set.all()]
        )

    def dehydrate_oficinas_municipio(self, obj):
        ano_corrente = timezone.localdate().year
        counters = Evento.objects.filter(
            status__in=[Evento.STATUS_AUTORIZADO, Evento.STATUS_REALIZADO],
            casa_anfitria__municipio=obj.casa.municipio,
            tipo_evento__categoria=TipoEvento.CATEGORIA_OFICINA,
        ).aggregate(
            total=Count("id"),
            no_ano=Count("id", filter=Q(data_inicio__year=ano_corrente)),
            dois_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 1),
            ),
            tres_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 2),
            ),
        )
        return _(
            (
                "Total: {total}, no ano corrente: {no_ano}, "
                "nos dois últimos anos: {dois_anos}, "
                "nos três últimos anos: {tres_anos}"
            ).format(**counters)
        )

    def dehydrate_oficinas_uf(sekf, obj):
        ano_corrente = timezone.localdate().year
        counters = Evento.objects.filter(
            status__in=[Evento.STATUS_AUTORIZADO, Evento.STATUS_REALIZADO],
            casa_anfitria__municipio__uf=obj.casa.municipio.uf,
            tipo_evento__categoria=TipoEvento.CATEGORIA_OFICINA,
        ).aggregate(
            total=Count("id"),
            no_ano=Count("id", filter=Q(data_inicio__year=ano_corrente)),
            dois_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 1),
            ),
            tres_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 2),
            ),
        )
        return _(
            (
                "Total: {total}, no ano corrente: {no_ano}, "
                "nos dois últimos anos: {dois_anos}, "
                "nos três últimos anos: {tres_anos}"
            ).format(**counters)
        )

    def dehydrate_oficinas_microrregiao(self, obj):
        ano_corrente = timezone.localdate().year
        counters = Evento.objects.filter(
            status__in=[Evento.STATUS_AUTORIZADO, Evento.STATUS_REALIZADO],
            casa_anfitria__municipio__microrregiao=obj.casa.municipio.microrregiao,
            tipo_evento__categoria=TipoEvento.CATEGORIA_OFICINA,
        ).aggregate(
            total=Count("id"),
            no_ano=Count("id", filter=Q(data_inicio__year=ano_corrente)),
            dois_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 1),
            ),
            tres_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 2),
            ),
        )
        return _(
            (
                "Total: {total}, no ano corrente: {no_ano}, "
                "nos dois últimos anos: {dois_anos}, "
                "nos três últimos anos: {tres_anos}"
            ).format(**counters)
        )

    def dehydrate_casa__municipio__uf__regiao(self, obj):
        return obj.casa.municipio.uf.get_regiao_display()


class EventoResource(ValueLabeledResource):
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
            "casa_anfitria__municipio__populacao",
            "casa_anfitria__municipio__uf__sigla",
            "casa_anfitria__municipio__uf__regiao",
            "casa_anfitria__cep",
            "casa_anfitria__email",
            "local",
            "observacao",
            "publico_alvo",
            "total_participantes",
            "inscritos_saberes",
            "aprovados_saberes",
            "data_sincronizacao",
            "status",
            "data_cancelamento",
            "motivo_cancelamento",
            "equipe__membro__nome_completo",
            "equipe__funcao__nome",
            "convite__casa__nome",
            "convite__casa__municipio__nome",
            "convite__casa__municipio__populacao",
            "convite__casa__municipio__uf__sigla",
            "convite__casa__municipio__uf__regiao",
            "convite__casa__cep",
            "convite__casa__email",
            "convite__qtde_participantes",
            "convite__nomes_participantes",
        )
        export_order = fields

    def dehydrate_tipo_evento__categoria(self, obj):
        return (
            dict(TipoEvento.CATEGORIA_CHOICES)[obj["tipo_evento__categoria"]]
            if obj["tipo_evento__categoria"]
            else None
        )

    def dehydrate_virtual(self, obj):
        return "Sim" if obj["virtual"] else "Não"

    def dehydrate_status(self, obj):
        return (
            dict(Evento.STATUS_CHOICES)[obj["status"]]
            if obj["status"]
            else None
        )

    def dehydrate_casa_anfitria__municipio__uf__regiao(self, obj):
        return (
            dict(UnidadeFederativa.REGIAO_CHOICES)[
                obj["casa_anfitria__municipio__uf__regiao"]
            ]
            if obj["casa_anfitria__municipio__uf__regiao"]
            else None
        )

    def dehydrate_convite__casa__municipio__uf__regiao(self, obj):
        return (
            dict(UnidadeFederativa.REGIAO_CHOICES)[
                obj["convite__casa__municipio__uf__regiao"]
            ]
            if obj["convite__casa__municipio__uf__regiao"]
            else None
        )


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


class AnexoSolicitacaoInline(admin.TabularInline):
    model = AnexoSolicitacao
    readonly_fields = ("data_pub",)


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
        "status",
        "senador",
        "get_act",
        "get_data_termino_vigencia_act",
        "data_pedido",
        "data_recebido_coperi",
        "get_oficinas",
        "get_municipio",
        "get_populacao",
        "get_oficinas_municipio",
        "get_uf",
        "get_oficinas_uf",
        "get_regiao",
        "get_microrregiao",
        "get_oficinas_microrregiao",
        "estimativa_casas",
        "estimativa_servidores",
    )
    list_display_links = ("casa",)
    list_filter = (
        "casa__municipio__uf",
        "casa__municipio__uf__regiao",
        "senador",
        "itemsolicitado__tipo_evento",
        "status",
        ActVigenteFilter,
    )
    list_select_related = ["casa", "casa__municipio", "casa__municipio__uf"]
    search_fields = (
        "casa__search_text",
        "casa__municipio__search_text",
        "casa__municipio__uf__search_text",
        "senador",
    )
    date_hierarchy = "data_pedido"
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "casa",
                    "senador",
                    "num_processo",
                    "descricao",
                    "data_pedido",
                    "data_recebido_coperi",
                ]
            },
        ),
        (
            _("Autorização"),
            {
                "fields": [
                    "status",
                    "servidor",
                    "data_analise",
                    "justificativa",
                ]
            },
        ),
        (
            _("Contato da Casa"),
            {
                "fields": [
                    "contato",
                    "email_contato",
                    "telefone_contato",
                    "whatsapp_contato",
                ]
            },
        ),
        (
            _("Participação esperada"),
            {"fields": ["estimativa_casas", "estimativa_servidores"]},
        ),
    )
    readonly_fields = ("servidor", "data_analise")
    inlines = (ItemSolicitadoInline, AnexoSolicitacaoInline)
    autocomplete_fields = ("casa",)

    def get_queryset(self, request):
        acts = Convenio.objects.filter(
            casa_legislativa=OuterRef("casa"),
            projeto__sigla="ACT",
            data_retorno_assinatura__lte=timezone.localdate(),
            data_termino_vigencia__gte=timezone.localdate(),
        ).order_by("data_termino_vigencia")
        qs = self.model._default_manager.get_queryset()
        qs = qs.annotate(
            act_id=Subquery(acts.values("id")[:1]),
            act_num=Subquery(acts.values("num_convenio")[:1]),
            act_data_termino_vigencia=Subquery(
                acts.values("data_termino_vigencia")[:1]
            ),
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Solicitacao.objects.get(id=obj.id)
        else:
            old_obj = obj
        if (
            obj.status != Solicitacao.STATUS_SOLICITADO
            and obj.status != old_obj.status
        ):
            obj.servidor = (
                request.user.servidor
                if hasattr(request.user, "servidor")
                else None
            )
            obj.data_analise = timezone.localtime()
        return super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model == ItemSolicitado:
            obj = form.instance
            instances = formset.save(commit=False)

            if hasattr(request.user, "servidor"):
                servidor = request.user.servidor
            else:
                servidor = None

            agora = timezone.localtime()

            for item in instances:
                if (
                    obj.status == Solicitacao.STATUS_SOLICITADO
                    and item.status != ItemSolicitado.STATUS_SOLICITADO
                ):
                    item.status = ItemSolicitado.STATUS_SOLICITADO
                    self.message_user(
                        request,
                        _(
                            f"O item {item} teve o status mudado para "
                            "SOLICITADO porque a solicitação ainda não foi "
                            "autorizada"
                        ),
                        messages.WARNING,
                    )
                if (
                    obj.status == Solicitacao.STATUS_REJEITADO
                    and item.status != ItemSolicitado.STATUS_REJEITADO
                ):
                    item.status = ItemSolicitado.STATUS_REJEITADO
                    self.message_user(
                        request,
                        _(
                            f"O item {item} teve o status mudado para "
                            "REJEITADO porque a solicitação inteira foi "
                            "rejeitada"
                        ),
                        messages.WARNING,
                    )
                if (
                    obj.status == Solicitacao.STATUS_CONCLUIDO
                    and item.status == ItemSolicitado.STATUS_SOLICITADO
                ):
                    item.status = ItemSolicitado.STATUS_REJEITADO
                    self.message_user(
                        request,
                        _(
                            f"O item {item} teve o status mudado para "
                            "REJEITADO porque a solicitação foi concluída e "
                            "ele ainda estava em aberto"
                        ),
                        messages.WARNING,
                    )

                if (
                    item.status == ItemSolicitado.STATUS_SOLICITADO
                    and item.evento is not None
                ):
                    item.evento.status = Evento.STATUS_PREVISTO
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
                            + datetime.timedelta(
                                days=item.tipo_evento.duracao
                            ),
                            casa_anfitria=item.solicitacao.casa,
                            observacao=_(
                                f"Autorizado por {servidor} com a justificativa '{item.justificativa}"
                            ),
                            status=Evento.STATUS_AUTORIZADO,
                            contato=item.solicitacao.contato,
                            telefone=item.solicitacao.telefone_contato,
                        )
                        self.message_user(
                            request,
                            _(f"Evento {item.evento} criado automaticamente."),
                            messages.INFO,
                        )
                    else:
                        item.evento.status = Evento.STATUS_AUTORIZADO
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

            if (
                obj.status == Solicitacao.STATUS_AUTORIZADO
                and not obj.itemsolicitado_set.filter(
                    status=ItemSolicitado.STATUS_SOLICITADO
                ).exists()
            ):
                obj.status = Solicitacao.STATUS_CONCLUIDO
                obj.save()
                self.message_user(
                    request,
                    _(
                        "Status da solicitação alterado automaticamente para "
                        "Concluído pois não há mais itens a serem analisados"
                    ),
                    messages.INFO,
                )

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
        description=_("Microrregião"), ordering="casa__municipio__microrregiao"
    )
    def get_microrregiao(self, obj):
        return obj.casa.municipio.microrregiao

    @admin.display(
        description=_("Oficinas atendidas/confirmadas na microrregião")
    )
    def get_oficinas_microrregiao(self, obj):
        ano_corrente = timezone.localdate().year
        counters = Evento.objects.filter(
            status__in=[Evento.STATUS_AUTORIZADO, Evento.STATUS_REALIZADO],
            casa_anfitria__municipio__microrregiao=obj.casa.municipio.microrregiao,
            tipo_evento__categoria=TipoEvento.CATEGORIA_OFICINA,
        ).aggregate(
            total=Count("id"),
            no_ano=Count("id", filter=Q(data_inicio__year=ano_corrente)),
            dois_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 1),
            ),
            tres_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 2),
            ),
        )
        return _(
            (
                "Total: {total}, no ano corrente: {no_ano}, "
                "nos dois últimos anos: {dois_anos}, "
                "nos três últimos anos: {tres_anos}"
            ).format(**counters)
        )

    @admin.display(
        description=_("População"), ordering="casa__municipio__populacao"
    )
    def get_populacao(self, obj):
        return obj.casa.municipio.populacao

    @admin.display(
        description=_("Oficinas atendidas/confirmadas no município")
    )
    def get_oficinas_municipio(self, obj):
        ano_corrente = timezone.localdate().year
        counters = Evento.objects.filter(
            status__in=[Evento.STATUS_AUTORIZADO, Evento.STATUS_REALIZADO],
            casa_anfitria__municipio=obj.casa.municipio,
            tipo_evento__categoria=TipoEvento.CATEGORIA_OFICINA,
        ).aggregate(
            total=Count("id"),
            no_ano=Count("id", filter=Q(data_inicio__year=ano_corrente)),
            dois_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 1),
            ),
            tres_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 2),
            ),
        )
        return _(
            (
                "Total: {total}, no ano corrente: {no_ano}, "
                "nos dois últimos anos: {dois_anos}, "
                "nos três últimos anos: {tres_anos}"
            ).format(**counters)
        )

    @admin.display(description=_("ACT vigente"), ordering="act_num")
    def get_act(self, obj):
        if obj.act_id:
            change_url = reverse(
                "admin:convenios_convenio_change", args=[obj.act_id]
            )
            return mark_safe(
                f"<a href='{change_url}' target='_blank'>" f"{obj.act_num}</a>"
            )
        return None

    @admin.display(description=_("Oficinas atendidas/confirmadas na UF"))
    def get_oficinas_uf(self, obj):
        ano_corrente = timezone.localdate().year
        counters = Evento.objects.filter(
            status__in=[Evento.STATUS_AUTORIZADO, Evento.STATUS_REALIZADO],
            casa_anfitria__municipio__uf=obj.casa.municipio.uf,
            tipo_evento__categoria=TipoEvento.CATEGORIA_OFICINA,
        ).aggregate(
            total=Count("id"),
            no_ano=Count("id", filter=Q(data_inicio__year=ano_corrente)),
            dois_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 1),
            ),
            tres_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 2),
            ),
        )
        return _(
            (
                "Total: {total}, no ano corrente: {no_ano}, "
                "nos dois últimos anos: {dois_anos}, "
                "nos três últimos anos: {tres_anos}"
            ).format(**counters)
        )

    @admin.display(
        description=_("Término vigência ACT"),
        ordering="act_data_termino_vigencia",
    )
    def get_data_termino_vigencia_act(self, obj):
        return obj.act_data_termino_vigencia


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
class EventoAdmin(CartExportReportMixin, admin.ModelAdmin):
    form = EventoAdminForm
    resource_class = EventoResource
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "tipo_evento",
                    "nome",
                    "turma",
                    "descricao",
                    "virtual",
                    "solicitante",
                    "num_processo",
                    "data_pedido",
                    "data_recebido_coperi",
                    "data_inicio",
                    "data_termino",
                    "carga_horaria",
                    "casa_anfitria",
                    "contato",
                    "telefone",
                    "observacao",
                )
            },
        ),
        (
            _("Status/participação"),
            {
                "fields": (
                    "status",
                    "total_participantes",
                    "inscritos_saberes",
                    "aprovados_saberes",
                    "data_sincronizacao",
                    "data_cancelamento",
                    "motivo_cancelamento",
                )
            },
        ),
        (
            _("Portal/Saberes"),
            {
                "fields": (
                    "publicar",
                    "publico_alvo",
                    "local",
                    "moodle_courseid",
                    "chave_inscricao",
                    "perfil_aluno",
                    "observacao_inscricao",
                    "contato_inscricao",
                    "telefone_inscricao",
                    "banner",
                )
            },
        ),
    )

    list_display = (
        "get_banner",
        "publicar",
        "get_tipo_evento",
        "nome",
        "turma",
        "status",
        "get_link_sigad",
        "data_inicio",
        "data_termino",
        "get_municipio",
        "get_uf",
        "get_regiao",
        "get_populacao",
        "solicitante",
        "total_participantes",
    )
    list_display_links = ("get_banner", "nome")
    list_filter = (
        "status",
        "publicar",
        ("num_processo", admin.EmptyFieldListFilter),
        "tipo_evento",
        "tipo_evento__categoria",
        "casa_anfitria__municipio__uf",
        "casa_anfitria__municipio__uf__regiao",
        ("data_inicio", DateRangeFilter),
        "virtual",
        "solicitante",
        ("moodle_courseid", admin.EmptyFieldListFilter),
        NumeroParticipantesFilter,
    )
    date_hierarchy = "data_inicio"
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
    readonly_fields = (
        "inscritos_saberes",
        "aprovados_saberes",
        "data_sincronizacao",
    )
    inlines = (
        EquipeInline,
        ConviteInline,
        ModuloInline,
        AnexoInline,
        CronogramaInline,
    )
    save_as = True
    reports = ["custos_eventos_report", "custos_servidor_report"]

    @admin.display(description=_("banner"))
    def get_banner(self, obj):
        if obj.banner:
            return mark_safe(
                f'<img src="{obj.banner.url}" width="60" height="60" />'
            )
        else:
            return ""

    @admin.display(description=_("SIGAD"), ordering="num_processo")
    def get_link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return mark_safe(obj.get_sigad_url())

    @admin.display(description=_("Tipo Evento"), ordering="tipo_evento__nome")
    def get_tipo_evento(self, obj):
        return obj.tipo_evento.nome

    @admin.display(
        description=_("Município"), ordering="casa_anfitria__municipio"
    )
    def get_municipio(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.municipio.nome
        else:
            return None

    @admin.display(
        description=_("UF"), ordering="casa_anfitria__municipio__uf"
    )
    def get_uf(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.municipio.uf.nome
        else:
            return None

    @admin.display(
        description=_("Região"),
        ordering="casa_anfitria__municipio__uf__regiao",
    )
    def get_regiao(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.municipio.uf.get_regiao_display()
        else:
            return None

    @admin.display(
        description=_("População"),
        ordering="casa_anfitria__municipio__populacao",
    )
    def get_populacao(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.municipio.populacao
        else:
            return None

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
            path(
                "<path:object_id>/custos/",
                self.admin_site.admin_view(self.custos_report),
                name="%s_%s_custos" % model_info,
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
            form = SelecionaModeloForm(
                initial={"modelo": ModeloDeclaracao.objects.first().id}
            )

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

    def custos_report(self, request, object_id):
        evento = get_object_or_404(Evento, id=object_id)
        change_url = (
            reverse(
                "admin:%s_%s_change" % self.get_model_info(), args=[object_id]
            )
            + "?"
            + self.get_preserved_filters(request)
        )

        if not evento.equipe_set.filter(
            Q(valor_diaria__gte=0) | Q(total_passagens__gte=0)
        ).exists():
            self.message_user(
                request,
                _("Não há valores de diárias e passagens para este evento"),
                messages.ERROR,
            )
            return redirect(change_url)

        membros = Equipe.objects.filter(evento=evento).annotate(
            antecedencia_passagens=(
                ExtractDay(F("evento__data_inicio") - F("emissao_passagens"))
            ),
            total_diarias=(F("qtde_diarias") * F("valor_diaria")),
            total_gasto=(F("total_diarias") + F("total_passagens")),
        )
        my_decimal_field = models.DecimalField(max_digits=14, decimal_places=2)
        total_equipe = membros.aggregate(
            num_membros=Count("membro_id", distinct=True),
            tot_qtde_diarias=Sum("qtde_diarias"),
            media_qtde_diarias=Cast(
                F("tot_qtde_diarias")
                / 1.0
                / F("num_membros"),  # divide por 1.0 para forçar float
                output_field=my_decimal_field,
            ),
            tot_valor_diarias=Sum("total_diarias"),
            media_diarias=Cast(
                F("tot_valor_diarias") / F("tot_qtde_diarias"),
                output_field=my_decimal_field,
            ),
            tot_passagens=Sum("total_passagens"),
            media_passagens=Cast(
                F("tot_passagens") / F("num_membros"),
                output_field=my_decimal_field,
            ),
            tot_gastos=Sum("total_gasto"),
            media_antecedencia=Avg("antecedencia_passagens"),
        )

        context = {
            "evento": evento,
            "membros": membros,
            "total_equipe": total_equipe,
        }

        return WeasyTemplateResponse(
            filename=f"custos{evento.nome.replace(' ','')}-{timezone.localdate()}.pdf",
            request=request,
            template="admin/eventos/evento/custos_report.html",
            context=context,
            content_type="application/pdf",
        )

    def custos_eventos_report(self, request):
        my_decimal_field = models.DecimalField(max_digits=14, decimal_places=2)
        equipe_qs = Equipe.objects.annotate(
            total_diarias=(F("qtde_diarias") * F("valor_diaria")),
            antecedencia=ExtractDay(
                F("evento__data_inicio") - F("emissao_passagens")
            ),
        )
        eventos = (
            self.get_queryset(request)
            .annotate(
                duracao_dias=(
                    ExtractDay(F("data_termino") - F("data_inicio")) + 1
                ),
                qtde_diarias=Sum("equipe__qtde_diarias"),
                vlr_tot_diarias=Sum(
                    F("equipe__qtde_diarias") * F("equipe__valor_diaria")
                ),
                vlr_tot_passagens=Sum("equipe__total_passagens"),
                custo_total=F("vlr_tot_diarias") + F("vlr_tot_passagens"),
                custo_medio_participante=Cast(
                    Case(
                        When(total_participantes__lte=0, then=0),
                        default=F("custo_total") / F("total_participantes"),
                        output_field=my_decimal_field,
                    ),
                    output_field=my_decimal_field,
                ),
                custo_medio_membro=Cast(
                    F("custo_total") / Count("equipe__membro"),
                    output_field=my_decimal_field,
                ),
                tot_membros=Count("equipe"),
            )
            .prefetch_related(
                Prefetch(
                    "equipe_set", queryset=equipe_qs, to_attr="equipe_ext"
                )
            )
        )
        resumo = eventos.aggregate(
            qtde_oficinas=Count("id"),
            tot_participantes=Sum("total_participantes"),
            media_participantes=Cast(
                1.0 * F("tot_participantes") / F("qtde_oficinas"),
                output_field=my_decimal_field,
            ),
            min_participantes=Min("total_participantes"),
            max_participantes=Max("total_participantes"),
            tot_servidores=Sum("tot_membros"),
            media_membros=Cast(
                1.0 * Sum("tot_membros") / F("qtde_oficinas"),
                output_field=my_decimal_field,
            ),
            min_membros=Min("tot_membros"),
            max_membros=Max("tot_membros"),
            tot_dias=Sum("duracao_dias"),
            media_dias=Cast(
                1.0 * F("tot_dias") / F("qtde_oficinas"),
                output_field=my_decimal_field,
            ),
            tot_diarias=Sum("qtde_diarias"),
            media_diarias=Cast(
                1.0 * F("tot_diarias") / F("qtde_oficinas"),
                output_field=my_decimal_field,
            ),
            tot_custo_total=Sum("custo_total"),
            tot_custo_diarias=Sum("vlr_tot_diarias"),
            tot_custo_passagens=Sum("vlr_tot_passagens"),
            media_custo_total=Cast(
                F("tot_custo_total") / F("qtde_oficinas"),
                output_field=my_decimal_field,
            ),
            media_custo_diarias=Cast(
                F("tot_custo_diarias") / F("qtde_oficinas"),
                output_field=my_decimal_field,
            ),
            media_custo_passagens=Cast(
                F("tot_custo_passagens") / F("qtde_oficinas"),
                output_field=my_decimal_field,
            ),
            media_custo_participantes=Cast(
                F("tot_custo_total") / F("tot_participantes"),
                output_field=my_decimal_field,
            ),
            media_custo_membro=Cast(
                F("tot_custo_total") / Sum("tot_membros"),
                output_field=my_decimal_field,
            ),
        )
        resumo.update(
            eventos.aggregate(
                media_antecedencia=Avg(
                    ExtractDay(
                        F("data_inicio") - F("equipe__emissao_passagens")
                    )
                ),
                min_antecedencia=Min(
                    ExtractDay(
                        F("data_inicio") - F("equipe__emissao_passagens")
                    )
                ),
                max_antecedencia=Max(
                    ExtractDay(
                        F("data_inicio") - F("equipe__emissao_passagens")
                    )
                ),
            )
        )

        f_valor_diarias = F("equipe__qtde_diarias") * F("equipe__valor_diaria")
        f_custo_total = (f_valor_diarias) + F("equipe__total_passagens")

        extrato = (
            self.get_queryset(request)
            .order_by("casa_anfitria__municipio__uf__regiao")
            .annotate(
                regiao=F("casa_anfitria__municipio__uf__regiao"),
                tot_diarias=Sum(f_valor_diarias),
                tot_passagens=Sum("equipe__total_passagens"),
                tot_custo=Sum(f_custo_total),
            )
            .values("regiao", "tot_diarias", "tot_passagens", "tot_custo")
        )

        df = (
            pd.DataFrame(extrato)
            .set_index("regiao")
            .groupby("regiao")
            .aggregate(["sum", "min", "max", "mean"])
            .fillna(0)
        )

        custos_regiao = [
            {
                "nome": nome,
                "extrato": df.loc[sigla] if sigla in df.index else None,
            }
            for sigla, nome in UnidadeFederativa.REGIAO_CHOICES
        ]

        context = {
            "eventos": eventos,
            "resumo": resumo,
            "custos_regiao": custos_regiao,
            "title": _("Custos por eventos"),
        }
        return WeasyTemplateResponse(
            filename=f"custos_eventos-{timezone.localdate()}.pdf",
            request=request,
            template="admin/eventos/custos_eventos_report.html",
            context=context,
            content_type="application/pdf",
        )

    custos_eventos_report.title = _("Custos por eventos")

    def custos_servidor_report(self, request):
        equipe_qs = Equipe.objects.filter(
            evento__in=self.get_queryset(request)
        )
        f_total_diarias = F("equipe_evento__qtde_diarias") * F(
            "equipe_evento__valor_diaria"
        )
        my_decimal_field = models.DecimalField(max_digits=14, decimal_places=2)

        servidores = (
            Servidor.objects.distinct()
            .filter(equipe_evento__evento__in=self.get_queryset(request))
            .prefetch_related(
                Prefetch(
                    "equipe_evento", queryset=equipe_qs, to_attr="equipe_ext"
                )
            )
            .annotate(
                qtde_eventos=Count("equipe_evento"),
                qtde_diarias=Sum("equipe_evento__qtde_diarias"),
                media_diarias=Cast(
                    Sum(f_total_diarias / F("equipe_evento__qtde_diarias")),
                    output_field=my_decimal_field,
                ),
                total_diarias=Sum(f_total_diarias),
                total_passagens=Sum("equipe_evento__total_passagens"),
                total_custo=Sum(
                    F("equipe_evento__total_passagens") + f_total_diarias
                ),
            )
        )
        totais = (
            Servidor.objects.distinct()
            .filter(equipe_evento__evento__in=self.get_queryset(request))
            .prefetch_related(
                Prefetch(
                    "equipe_evento", queryset=equipe_qs, to_attr="equipe_ext"
                )
            )
            .aggregate(
                qtde_eventos=Count("equipe_evento"),
                qtde_diarias=Sum("equipe_evento__qtde_diarias"),
                media_diarias=Cast(
                    Avg(f_total_diarias / F("equipe_evento__qtde_diarias")),
                    output_field=my_decimal_field,
                ),
                total_diarias=Sum(f_total_diarias),
                total_passagens=Sum("equipe_evento__total_passagens"),
                total_custo=Sum(
                    F("equipe_evento__total_passagens") + f_total_diarias
                ),
            )
        )
        context = {
            "servidores": servidores,
            "totais": totais,
            "title": _("Custos por servidor"),
        }
        return WeasyTemplateResponse(
            filename=f"custos_servidor-{timezone.localdate()}.pdf",
            request=request,
            template="admin/eventos/custos_servidor_report.html",
            context=context,
            content_type="application/pdf",
        )

    custos_servidor_report.title = _("Custos por servidor")

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

        try:
            evento.sincroniza_saberes()
        except Evento.SaberesSyncException as e:
            self.message_user(
                request,
                _(f"Erro ao sincronizar dados do Saberes: '{e.message}'"),
                level=messages.ERROR,
            )
            return redirect(change_url)

        self.message_user(
            request,
            _(
                f"Foram encontrados {evento.inscritos_saberes} alunos "
                f"no Saberes. Destes, {evento.aprovados_saberes} concluíram."
            ),
            level=messages.SUCCESS,
        )

        return redirect(change_url)
