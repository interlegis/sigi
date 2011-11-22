# -*- coding: utf-8 -*-
from django.contrib import admin
from eav.admin import BaseEntityAdmin, BaseSchemaAdmin
from sigi.apps.diagnosticos.models import Diagnostico, Pergunta, Escolha, Equipe, Anexo
from sigi.apps.diagnosticos.forms import DiagnosticoForm

class EquipeInline(admin.TabularInline):
    model = Equipe
    extra = 4

class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub',]

class AnexoAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_pub'
    exclude = ['data_pub',]
    list_display = ('arquivo', 'descricao', 'data_pub', 'diagnostico')
    raw_id_fields = ('diagnostico',)
    search_fields = ('descricao', 'diagnostico__id', 'arquivo',
                     'diagnostico__casa_legislativa__nome')

class DiagnosticoAdmin(BaseEntityAdmin):
    form = DiagnosticoForm
    inlines = (EquipeInline, AnexosInline)
    raw_id_fields = ('casa_legislativa',)

admin.site.register(Diagnostico, DiagnosticoAdmin)
admin.site.register(Pergunta, BaseSchemaAdmin)
admin.site.register(Escolha)
admin.site.register(Anexo, AnexoAdmin)
