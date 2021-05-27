# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from sigi.apps.contatos.models import Endereco, Telefone
from sigi.apps.servidores.models import Servidor, Servico
from sigi.apps.utils.admin_widgets import AdminImageWidget
from sigi.apps.utils.base_admin import BaseModelAdmin
from sigi.apps.utils.filters import AlphabeticFilter

class ServidorFilter(AlphabeticFilter):
    title = _(u'Nome do Servidor')
    parameter_name = 'servidor__nome_completo'

class ServicoFilter(admin.SimpleListFilter):
    title = _(u"Subordinados à")
    parameter_name = 'subordinado__id__exact'

    def lookups(self, request, model_admin):
        return ([('None', _(u"Nenhum"))] +
                [(s.id, s.nome) for s in Servico.objects.exclude(servico=None)])

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "None":
                queryset = queryset.filter(subordinado=None)
            else:
                queryset = queryset.filter(subordinado__id=self.value())
        return queryset


class ServicoInline(admin.TabularInline):
    model = Servico
    fields = ['nome', 'sigla', 'responsavel',]

class ServidorInline(admin.TabularInline):
    model = Servidor
    fields = ('imagem_foto', 'nome_completo', 'is_active', )
    readonly_fields = ('imagem_foto', 'nome_completo', 'is_active', )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj):
        return False

    def imagem_foto(sels, servidor):
        if servidor.foto:
            return u'<img src="{url}" style="height: 60px; width: 60px; border-radius: 50%;">'.format(url=servidor.foto.url)
        else:
            return u""
    imagem_foto.short_description = _(u"foto")
    imagem_foto.allow_tags = True

    def is_active(self, servidor):
        if servidor.user:
            return servidor.user.is_active
        else:
            return False
    is_active.admin_order_field = 'user__is_active'
    is_active.boolean = True
    is_active.short_description = _(u'ativo')


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'nome', 'subordinado', 'responsavel']
    list_filter = [ServicoFilter,]
    search_fields = ['nome', 'sigla',]
    inlines = [ServicoInline, ServidorInline,]

@admin.register(Servidor)
class ServidorAdmin(BaseModelAdmin):
    list_display = ('imagem_foto', 'nome_completo', 'is_active', 'servico', )
    list_display_links = ('imagem_foto', 'nome_completo',)
    list_filter = ('user__is_active', 'externo', 'servico')
    search_fields = ('nome_completo', 'user__email', 'user__first_name',
                     'user__last_name', 'user__username', 'servico__nome',
                     'servico__sigla')
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {
            'fields': ('user', 'nome_completo', 'foto', 'servico',)
        }),
        (_(u"outros órgãos"), {
            'fields': ('externo', 'orgao_origem', 'qualificacoes'),
        }),
    )

    def lookup_allowed(self, lookup, value):
        return super(ServidorAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['user__is_active__exact']

    # def has_add_permission(self, request):
    #     return False

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'foto':
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(ServidorAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def is_active(self, servidor):
        if servidor.user:
            return servidor.user.is_active
        else:
            return False
    is_active.admin_order_field = 'user__is_active'
    is_active.boolean = True
    is_active.short_description = _(u'ativo')

    def imagem_foto(sels, servidor):
        if servidor.foto:
            return u'<img src="{url}" style="height: 60px; width: 60px; border-radius: 50%;">'.format(url=servidor.foto.url)
        else:
            return u""
    imagem_foto.short_description = _(u"foto")
    imagem_foto.allow_tags = True