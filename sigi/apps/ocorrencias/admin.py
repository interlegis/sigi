# -*- coding: utf-8 -*-
from django.contrib import admin
from eav.admin import BaseEntityAdmin, BaseSchemaAdmin
from sigi.apps.ocorrencias.models import Ocorrencia, Comentario, Anexo, Categoria

class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 1

class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub',]

class AnexoAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_pub'
    exclude = ['data_pub',]
    list_display = ('arquivo', 'descricao', 'data_pub', 'ocorrencia')
    raw_id_fields = ('ocorrencia',)
    search_fields = ('descricao', 'ocorrencia__id', 'arquivo',
                     'ocorrencia__casa_legislativa__nome')

class OcorrenciaAdmin(BaseEntityAdmin):
    inlines = (ComentarioInline, AnexosInline)
    raw_id_fields = ('casa_legislativa',)

admin.site.register(Ocorrencia, OcorrenciaAdmin)
admin.site.register(Anexo, AnexoAdmin)
admin.site.register(Categoria)
