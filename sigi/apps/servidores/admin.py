# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic

from sigi.apps.utils.admin_widgets import AdminImageWidget
from sigi.apps.servidores.models import Servidor, Funcao, Licenca, Ferias
from sigi.apps.contatos.models import Endereco, Telefone
from sigi.apps.servidores.forms import FeriasForm, LicencaForm, FuncaoForm

class FuncaoInline(admin.TabularInline):
    model = Funcao
    extra = 1

class FuncaoAdmin(admin.ModelAdmin):
    form = FuncaoForm
    list_display = ('servidor', 'funcao', 'cargo','inicio_funcao', 'fim_funcao')
    list_filter  = ('inicio_funcao', 'fim_funcao')
    search_fields = ('funcao', 'cargo', 'descricao',
                     'servidor__nome_completo', 'servidor__obs', 'servidor__apontamentos',
                     'servidor__user__email', 'servidor__user__first_name',
                     'servidor__user__last_name', 'servidor__user__username')

class FeriasInline(admin.TabularInline):
    model = Ferias
    extra = 1

class FeriasAdmin(admin.ModelAdmin):
    form = FeriasForm
    list_display = ('servidor', 'inicio_ferias', 'fim_ferias')
    list_filter  = ('servidor', 'inicio_ferias', 'fim_ferias')
    search_fields = ('obs',
                     'servidor__nome_completo', 'servidor__obs', 'servidor__apontamentos',
                     'servidor__user__email', 'servidor__user__first_name',
                     'servidor__user__last_name', 'servidor__user__username')


class LicencaInline(admin.TabularInline):
    model = Licenca
    extra = 1

class LicencaAdmin(admin.ModelAdmin):
    form = LicencaForm
    list_display = ('servidor', 'inicio_licenca', 'fim_licenca')
    list_filter  = ('servidor', 'inicio_licenca', 'fim_licenca')
    search_fields = ('obs',
                     'servidor__nome_completo', 'servidor__obs', 'servidor__apontamentos',
                     'servidor__user__email', 'servidor__user__first_name',
                     'servidor__user__last_name', 'servidor__user__username')

class EnderecoInline(generic.GenericTabularInline):
    model = Endereco
    extra = 1
    raw_id_fields = ('municipio',)

class TelefonesInline(generic.GenericTabularInline):
    extra = 1
    model = Telefone

class ServidorAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'servico')
    list_filter  = ('sexo', 'servico')
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
        'fields': ('nome_completo', 'foto', 'email_pessoal', 'rg', 'cpf', 'sexo', 'data_nascimento', 'matricula', 'ramal')
      }),
      ('Origem', {
        'fields': ('turno',),
      }),
      (u'Observações', {
        'fields': ('apontamentos', 'obs'),
      }),
      #('Advanced options', {
      #  'classes': ('collapse',),
      #  'fields': ('enable_comments', 'registration_required', 'template_name')
      #}),
    )

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
