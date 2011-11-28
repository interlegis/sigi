# -*- coding: utf-8 -*-
from django.contrib import admin
from eav.admin import BaseEntityAdmin, BaseSchemaAdmin
from sigi.apps.diagnosticos.models import Diagnostico, Pergunta, Escolha, Equipe, Anexo, Categoria
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


# Ação de alterar o status das publicações no modo Draft.
def alterar_status_publicacao(modeladmin, request, queryset):
    queryset.update(status=True)
alterar_status_publicacao.short_description = u"""
    Publicar diagnósticos selecionados"""

class DiagnosticoAdmin(BaseEntityAdmin):
    form = DiagnosticoForm
    date_hierarchy = 'data_questionario'
    actions = [alterar_status_publicacao]
    inlines = (EquipeInline, AnexosInline)
    raw_id_fields = ('casa_legislativa', 'responsavel')

    eav_fieldsets = [
        (u'00. Identificação do Diagnóstico', {'fields': ('responsavel', 'data_visita', 'data_questionario', 'data_relatorio_questionario')}),
        (u'01. Identificação da Casa Legislativa', {'fields': ('casa_legislativa',)}),
        (u'02. Identificação de Competências da Casa Legislativa', {'fields': ()})
      ]
    # separa as perguntas (title e name) dentro das categorias existente para ordenar
    dict_categoria = {}
    for pergunta in Pergunta.objects.all():
        if pergunta.categoria:
            categoria = pergunta.categoria.nome
        else:
            categoria = None

        if categoria in dict_categoria.keys():
            dict_categoria[categoria].append((pergunta.title.strip(), pergunta.name))
        else:
            dict_categoria[categoria] = [(pergunta.title.strip(), pergunta.name)]

    # popula o eav fieldset ordenando as categorias e as perguntas
    # para ser exibido no admin
    for categoria in sorted(dict_categoria.keys()):
        # ordena as perguntas pelo title e utiliza o name no fieldset
        perguntas = [pergunta[1] for pergunta in sorted(dict_categoria[categoria])]

        eav_fieldsets.append((categoria, {
          'fields': tuple(perguntas),
          'classes': ['collapse']
          }))


class PerguntaAdmin (BaseSchemaAdmin):
    search_fields = ('title', 'help_text', 'name',)
    list_display = ('title', 'categoria', 'datatype', 'help_text', 'required')
    list_filter = ('datatype', 'categoria', 'required')

class EscolhaAdmin(admin.ModelAdmin):
    search_fields = ('title',) 
    list_display = ('title', 'schema', 'schema_to_open')
    raw_id_fields = ('schema', 'schema_to_open')
    ordering = ('schema', 'title')

admin.site.register(Diagnostico, DiagnosticoAdmin)
admin.site.register(Pergunta, PerguntaAdmin)
admin.site.register(Escolha, EscolhaAdmin)
admin.site.register(Anexo, AnexoAdmin)
admin.site.register(Categoria)
