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

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'nome', 'subordinado', 'responsavel']
    list_filter = ['subordinado',]
    search_fields = ['nome', 'sigla',]

@admin.register(Servidor)
class ServidorAdmin(BaseModelAdmin):
    list_display = ('foto', 'nome_completo', 'is_active', 'servico', )
    list_filter = ('user__is_active', 'servico',)
    search_fields = ('nome_completo', 'user__email', 'user__first_name',
                     'user__last_name', 'user__username', 'servico__nome',
                     'servico__sigla')
    raw_id_fields = ('user',)
    fields = ['user', 'nome_completo', 'foto', 'servico',]

    def lookup_allowed(self, lookup, value):
        return super(ServidorAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['user__is_active__exact']

    def has_add_permission(self, request):
        return False

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'foto':
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(ServidorAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def is_active(self, servidor):
        return servidor.user.is_active
    is_active.admin_order_field = 'user__is_active'
    is_active.boolean = True
    is_active.short_description = _(u'ativo')