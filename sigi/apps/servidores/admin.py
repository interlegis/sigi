from django.db import models
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from sigi.apps.servidores.models import Servidor, Servico
from sigi.apps.servidores.filters import ServicoFilter


class ServicoInline(admin.TabularInline):
    model = Servico
    fields = ['nome', 'sigla', 'responsavel',]
    autocomplete_fields = ['responsavel',]

class ServidorInline(admin.TabularInline):
    model = Servidor
    fields = ('imagem_foto', 'nome_completo', 'is_active', )
    readonly_fields = ('imagem_foto', 'nome_completo', 'is_active', )

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False

    def imagem_foto(sels, servidor):
        if servidor.foto:
            return mark_safe(
                f'<img src="{servidor.foto.url}" style="height: 60px; '
                f'width: 60px; border-radius: 50%;">'
            )
        else:
            return ""
    imagem_foto.short_description = _("foto")

    def is_active(self, servidor):
        if servidor.user:
            return servidor.user.is_active
        else:
            return False
    is_active.admin_order_field = 'user__is_active'
    is_active.boolean = True
    is_active.short_description = _('ativo')

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'nome', 'subordinado', 'responsavel']
    list_filter = [ServicoFilter,]
    search_fields = ['nome', 'sigla',]
    autocomplete_fields = ['subordinado', 'responsavel',]
    inlines = [ServicoInline, ServidorInline,]

@admin.register(Servidor)
class ServidorAdmin(admin.ModelAdmin):
    list_display = ('imagem_foto', 'nome_completo', 'is_active', 'servico', )
    list_display_links = ('imagem_foto', 'nome_completo',)
    list_filter = ('user__is_active', 'externo', 'servico',)
    search_fields = ('nome_completo', 'user__email', 'user__first_name',
                     'user__last_name', 'user__username', 'servico__nome',
                     'servico__sigla')
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {
            'fields': ('user', 'nome_completo', 'foto', 'servico',)
        }),
        (_("outros órgãos"), {
            'fields': ('externo', 'orgao_origem', 'qualificacoes'),
        }),
    )

    def lookup_allowed(self, lookup, value):
        return super(ServidorAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['user__is_active__exact']

    def is_active(self, servidor):
        if servidor.user:
            return servidor.user.is_active
        else:
            return False
    is_active.admin_order_field = 'user__is_active'
    is_active.boolean = True
    is_active.short_description = _('ativo')

    def imagem_foto(sels, servidor):
        if servidor.foto:
            return mark_safe(
                f'<img src="{servidor.foto.url}" style="height: 60px; '
                f'width: 60px; border-radius: 50%;">'
            )
        else:
            return ""
    imagem_foto.short_description = _("foto")