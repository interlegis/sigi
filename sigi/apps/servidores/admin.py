# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic

from sigi.apps.utils.admin_widgets import AdminImageWidget
from sigi.apps.servidores.models import Servidor, Funcao, Licenca, Ferias, Servico, Subsecretaria
from sigi.apps.contatos.models import Endereco, Telefone
from sigi.apps.servidores.forms import FeriasForm, LicencaForm, FuncaoForm

class FuncaoAdmin(admin.ModelAdmin):
    form = FuncaoForm
    list_display = ('servidor', 'funcao', 'cargo','inicio_funcao', 'fim_funcao')
    list_filter  = ('inicio_funcao', 'fim_funcao')
    search_fields = ('funcao', 'cargo', 'descricao',
                     'servidor__nome_completo', 'servidor__obs', 'servidor__apontamentos',
                     'servidor__user__email', 'servidor__user__first_name',
                     'servidor__user__last_name', 'servidor__user__username')

class FeriasAdmin(admin.ModelAdmin):
    form = FeriasForm
    list_display = ('servidor', 'inicio_ferias', 'fim_ferias')
    list_filter  = ('inicio_ferias', 'fim_ferias')
    search_fields = ('obs',
                     'servidor__nome_completo', 'servidor__email_pessoal',
                     'servidor__user__email', 'servidor__user__username')

class LicencaAdmin(admin.ModelAdmin):
    form = LicencaForm
    list_display = ('servidor', 'inicio_licenca', 'fim_licenca')
    list_filter  = ('servidor', 'inicio_licenca', 'fim_licenca')
    search_fields = ('obs',
                     'servidor__nome_completo', 'servidor__email_pessoal',
                     'servidor__user__email', 'servidor__user__username')

class EnderecoInline(generic.GenericStackedInline):
    model = Endereco
    extra = 0
    raw_id_fields = ('municipio',)

class TelefonesInline(generic.GenericTabularInline):
    extra = 1
    model = Telefone

class ServidorAdmin(admin.ModelAdmin):
    def is_active(self, servidor):
        return servidor.user.is_active
    is_active.admin_order_field = 'user__is_active'
    is_active.boolean = True
    is_active.short_description = 'ativo'

    list_display = ('nome_completo', 'is_active', 'foto', 'servico', )
    list_filter  = ('user__is_active', 'sexo', 'servico',)
    search_fields = ('nome_completo', 'obs', 'apontamentos',
                     'user__email', 'user__first_name',
                     'user__last_name', 'user__username')
    raw_id_fields = ('user',)
    inlines= (TelefonesInline,EnderecoInline)
    fieldsets = (
      (u'Autenticação', {
        'fields': ('user',),
      }),
      ('Cadastro', {
        'fields': ('nome_completo', 'foto', 'email_pessoal', 'rg', 'cpf', 'sexo', 'data_nascimento', 'matricula', 'ramal', 'data_nomeacao', 'ato_numero', 'ato_exoneracao')
      }),
      ('Lotação', {
        'fields': ('servico', 'turno', 'de_fora'),
      }),
      (u'Observações', {
        'fields': ('apontamentos', 'obs'),
      }),
    )

    def lookup_allowed(self, lookup, value):
        return super(ServidorAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['user__is_active__exact']

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'foto':
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(ServidorAdmin,self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Servidor, ServidorAdmin)
admin.site.register(Funcao, FuncaoAdmin)
admin.site.register(Ferias, FeriasAdmin)
admin.site.register(Licenca, LicencaAdmin)
admin.site.register(Servico)
admin.site.register(Subsecretaria)