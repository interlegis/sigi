from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

from sigi.apps.ocorrencias.filters import ServidorRegistroFilter
from sigi.apps.ocorrencias.models import (
    Ocorrencia,
    Comentario,
    Anexo,
    Categoria,
    TipoContato,
)
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils.mixins import ReturnMixin
from sigi.apps.casas.admin import GerentesInterlegisFilter


class ComentarioViewInline(admin.TabularInline):
    model = Comentario
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name = _("Comentário anterior")
    verbose_name_plural = _("Comentários anteriores")
    fields = (
        "usuario",
        "data_criacao",
        "novo_status",
        "descricao",
    )
    readonly_fields = fields


class ComentarioInline(admin.StackedInline):
    model = Comentario
    extra = 1
    verbose_name = _("Comentário novo")
    verbose_name_plural = _("Comentários novos")
    fields = (
        "novo_status",
        "descricao",
    )

    def get_queryset(self, queryset):
        return self.model.objects.none()


class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    readonly_fields = [
        "data_pub",
    ]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo")
    list_filter = ("tipo",)
    search_fields = ("nome", "descricao")


@admin.register(TipoContato)
class TipoContatoAdmin(admin.ModelAdmin):
    list_display = ("descricao",)
    search_fields = ("descricao",)


@admin.register(Ocorrencia)
class OcorrenciaAdmin(ReturnMixin, admin.ModelAdmin):
    list_display = (
        "data_criacao",
        "casa_legislativa",
        "get_municipio",
        "get_uf",
        "assunto",
        "prioridade",
        "status",
        "data_modificacao",
    )
    list_filter = (
        "status",
        "prioridade",
        "categoria__nome",
        ("casa_legislativa__gerentes_interlegis", GerentesInterlegisFilter),
        ("servidor_registro", ServidorRegistroFilter),
    )
    search_fields = (
        "casa_legislativa__search_text",
        "assunto",
        "servidor_registro__nome_completo",
        "descricao",
        "resolucao",
        "ticket",
    )
    date_hierarchy = "data_criacao"
    fields = (
        "casa_legislativa",
        "categoria",
        "tipo_contato",
        "assunto",
        "status",
        "prioridade",
        "ticket",
        "descricao",
        "servidor_registro",
        "resolucao",
    )
    readonly_fields = ("servidor_registro",)
    inlines = (
        ComentarioViewInline,
        ComentarioInline,
        AnexosInline,
    )
    autocomplete_fields = ("casa_legislativa", "categoria", "tipo_contato")

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            self.fields = (
                "casa_legislativa",
                "categoria",
                "tipo_contato",
                "assunto",
                "prioridade",
                "ticket",
                "descricao",
                "resolucao",
            )
        else:
            self.fields = (
                "casa_legislativa",
                "categoria",
                "tipo_contato",
                "assunto",
                "status",
                "prioridade",
                "ticket",
                "descricao",
                "servidor_registro",
                "resolucao",
            )

        return super().get_fieldsets(request, obj)

    def has_add_permission(self, request):
        if Servidor.objects.filter(user=request.user).exists():
            return super().has_add_permission(request)
        return False

    def has_change_permission(self, request, *args, **kwargs):
        if Servidor.objects.filter(user=request.user).exists():
            return super().has_change_permission(request, *args, **kwargs)
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.servidor_registro = Servidor.objects.get(user=request.user)
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Comentario):
                instance.usuario = request.user.servidor
            instance.save()
        super(OcorrenciaAdmin, self).save_formset(
            request, form, formset, change
        )

    def get_uf(self, obj):
        return mark_safe(obj.casa_legislativa.municipio.uf)

    get_uf.short_description = _("UF")

    def get_municipio(self, obj):
        return mark_safe(obj.casa_legislativa.municipio.nome)

    get_municipio.short_description = _("Município")
    get_municipio.admin_order_field = "casa_legislativa__municipio__nome"
