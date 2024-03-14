from typing import Any
from django.contrib import admin, messages
from django.http.request import HttpRequest
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, ngettext
from django.shortcuts import get_object_or_404, redirect
from import_export.fields import Field
from sigi.apps.espacos.models import (
    Espaco,
    Recurso,
    Reserva,
    RecursoSolicitado,
)
from sigi.apps.espacos.forms import ReservaAdminForm
from sigi.apps.utils.mixins import CartExportMixin, LabeledResourse


class ReservaResource(LabeledResourse):
    recursos_solicitados = Field(column_name="recursos solicitados")

    class Meta:
        model = Reserva
        fields = (
            "status",
            "espaco__sigla",
            "espaco__nome",
            "proposito",
            "inicio",
            "termino",
            "informacoes",
            "solicitante",
            "contato",
            "telefone_contato",
        )
        export_order = fields

    def dehydrate_status(self, obj):
        return obj.get_status_display()

    def dehydrate_recursos_solicitados(self, obj):
        return ", ".join(
            [
                _(f"{r.quantidade} {r.recurso.nome}")
                for r in obj.recursosolicitado_set.all()
            ]
        )


class RecursoSolicitadoInline(admin.TabularInline):
    model = RecursoSolicitado
    autocomplete_fields = [
        "recurso",
    ]


@admin.register(Espaco)
class EspacoAdmin(admin.ModelAdmin):
    list_display = ["sigla", "nome"]
    search_fields = ["sigla", "nome"]


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ["sigla", "nome"]
    search_fields = ["sigla", "nome"]


@admin.register(Reserva)
class ReservaAdmin(CartExportMixin, admin.ModelAdmin):
    form = ReservaAdminForm
    resource_classes = [ReservaResource]
    list_display = [
        "status",
        "proposito",
        "get_link_sigad",
        "get_espaco",
        "data_inicio",
        "data_termino",
        "hora_inicio",
        "hora_termino",
        "virtual",
        "solicitante",
        "contato",
        "telefone_contato",
    ]
    list_display_links = ["status", "proposito"]
    list_filter = [
        "espaco",
        "virtual",
        "status",
        ("id_reserva", admin.EmptyFieldListFilter),
    ]
    search_fields = [
        "proposito",
        "espaco__nome",
        "espaco__sigla",
        "num_processo",
    ]
    date_hierarchy = "data_inicio"
    fieldsets = [
        (None, {"fields": ("status",)}),
        (
            _("Solicitação"),
            {
                "fields": (
                    "espaco",
                    "evento",
                    "proposito",
                    "num_processo",
                    "virtual",
                    "data_pedido",
                    "total_participantes",
                )
            },
        ),
        (
            _("Detalhes"),
            {
                "fields": (
                    ("data_inicio", "hora_inicio"),
                    ("data_termino", "hora_termino"),
                    "informacoes",
                )
            },
        ),
        (
            _("Contato"),
            {"fields": ("solicitante", "contato", "telefone_contato")},
        ),
        (
            _("Integração com sistema de reservas"),
            {"fields": ("id_reserva", "data_ult_atualizacao")},
        ),
    ]
    autocomplete_fields = ["espaco"]
    readonly_fields = ("evento", "id_reserva", "data_ult_atualizacao")
    inlines = [RecursoSolicitadoInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and hasattr(obj, "evento"):
            if not hasattr(self, "_readonly_evento_alerted"):
                self.message_user(
                    request,
                    _(
                        f"Esta reserva está vinculada ao evento '{obj.evento}'. "
                        "Apenas os recursos solicitados podem ser editados. "
                        "Os demais campos devem ser alterados no evento."
                    ),
                    level=messages.ERROR,
                )
                self._readonly_evento_alerted = True
            return self.get_fields(request)
        return super().get_readonly_fields(request, obj)

    @admin.display(description=_("Espaço"), ordering="espaco")
    def get_espaco(self, obj):
        return obj.espaco.sigla

    @admin.display(description=_("SIGAD"), ordering="num_processo")
    def get_link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return mark_safe(obj.get_sigad_url())
