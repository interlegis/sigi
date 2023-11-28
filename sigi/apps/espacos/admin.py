from django.contrib import admin, messages
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
    resource_classes = [ReservaResource]
    list_display = [
        "get_status",
        "proposito",
        "get_link_sigad",
        "get_espaco",
        "inicio",
        "termino",
        "virtual",
        "solicitante",
        "contato",
        "telefone_contato",
    ]
    list_display_links = ["get_status", "proposito"]
    list_filter = ["status", "espaco", "virtual"]
    search_fields = [
        "proposito",
        "espaco__nome",
        "espaco__sigla",
        "num_processo",
    ]
    date_hierarchy = "inicio"
    actions = ["cancelar_action", "reativar_action"]
    fieldsets = [
        (None, {"fields": ("status",)}),
        (
            _("Solicitação"),
            {
                "fields": (
                    "espaco",
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
                    "inicio",
                    "termino",
                    "informacoes",
                )
            },
        ),
        (
            _("Contato"),
            {"fields": ("solicitante", "contato", "telefone_contato")},
        ),
    ]
    autocomplete_fields = ["espaco"]
    readonly_fields = ("status",)
    inlines = [RecursoSolicitadoInline]

    def get_urls(self):
        urls = super().get_urls()
        model_info = self.get_model_info()
        my_urls = [
            path(
                "<path:object_id>/cancel/",
                self.admin_site.admin_view(self.cancelar_reserva),
                name="%s_%s_cancel" % model_info,
            )
        ]
        return my_urls + urls

    @admin.display(description=_("Status"), ordering="status", boolean=True)
    def get_status(self, obj):
        return obj.status == Reserva.STATUS_ATIVO

    @admin.display(description=_("Espaço"), ordering="espaco")
    def get_espaco(self, obj):
        return obj.espaco.sigla

    @admin.display(description=_("SIGAD"), ordering="num_processo")
    def get_link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return mark_safe(obj.get_sigad_url())

    def cancelar_reserva(self, request, object_id):
        reserva = get_object_or_404(Reserva, id=object_id)
        reserva.status = Reserva.STATUS_CANCELADO
        reserva.save()
        return redirect(
            reverse(
                "admin:%s_%s_change" % self.get_model_info(), args=[object_id]
            )
            + "?"
            + self.get_preserved_filters(request)
        )

    @admin.action(description=_("Cancelar as reservas selecionadas"))
    def cancelar_action(self, request, queryset):
        count = queryset.update(status=Reserva.STATUS_CANCELADO)
        self.message_user(
            request,
            ngettext(
                "Uma reserva cancelada", f"{count} reservas canceladas", count
            ),
            messages.SUCCESS,
        )

    @admin.action(description=_("Reativar as reservas selecionadas"))
    def reativar_action(self, request, queryset):
        count = queryset.update(status=Reserva.STATUS_ATIVO)
        self.message_user(
            request,
            ngettext(
                "Uma reserva reativada", f"{count} reservas reativadas", count
            ),
            messages.SUCCESS,
        )
