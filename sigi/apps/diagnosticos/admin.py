# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import admin
from eav.admin import BaseEntityAdmin, BaseSchemaAdmin
from sigi.apps.diagnosticos.models import Diagnostico, Pergunta, Escolha, Equipe, Anexo, Categoria
from sigi.apps.diagnosticos.forms import DiagnosticoForm
from sigi.apps.contatos.models import UnidadeFederativa

def publicar_diagnostico(self, request, queryset):
    for registro in queryset:
        diagnostico = Diagnostico.objects.get(pk=registro.id)
        diagnostico.publicado = True
        diagnostico.data_publicacao= datetime.now()
        diagnostico.save()

        # Enviando o email avisando que o diagnóstico foi publicado
        email = diagnostico.responsavel.user.email
        if email:
          diagnostico.email_diagnostico_publicado(email, request.get_host())
    self.message_user(request, "Diagnóstico(s) publicado(s) com sucesso!")
publicar_diagnostico.short_description = u"""
    Definir diagnósticos como publicado"""


def despublicar_diagnostico(self, request, queryset):
    queryset.update(publicado=False)
despublicar_diagnostico.short_description = u"""
    Definir diagnósticos como não publicado"""

class EquipeInline(admin.TabularInline):
    model = Equipe

class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub', ]

class AnexoAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_pub'
    exclude = ['data_pub', ]
    list_display = ('arquivo', 'descricao', 'data_pub', 'diagnostico')
    raw_id_fields = ('diagnostico',)
    search_fields = ('descricao', 'diagnostico__id', 'arquivo',
                     'diagnostico__casa_legislativa__nome')

class DiagnosticoAdmin(BaseEntityAdmin):
    form = DiagnosticoForm
    actions = [publicar_diagnostico, despublicar_diagnostico]
    inlines = (EquipeInline, AnexosInline)
    search_fields = ('casa_legislativa__nome',)
    list_display = ('casa_legislativa','getUf', 'data_visita_inicio', 'data_visita_fim', 'responsavel', 'publicado')
    list_filter  = ('publicado', 'data_publicacao', 'data_visita_inicio', 'data_visita_fim')
    raw_id_fields = ('casa_legislativa',)

    eav_fieldsets = [
        (u'00. Identificação do Diagnóstico', {'fields': ('responsavel', 'data_visita_inicio', 'data_visita_fim',)}),
        (u'01. Identificação da Casa Legislativa', {'fields': ('casa_legislativa',)}),
        (u'02. Identificação de Competências da Casa Legislativa', {'fields': ()})
      ]

    # popula o eav fieldsets ordenando as categorias e as perguntas
    # para serem exibidas no admin
    for categoria in Categoria.objects.all():
        # ordena as perguntas pelo title e utiliza o name no fieldset
        perguntas_by_title = [(p.title, p.name) for p in categoria.perguntas.all()]
        perguntas = [pergunta[1] for pergunta in sorted(perguntas_by_title)]

        eav_fieldsets.append((categoria, {
          'fields': tuple(perguntas),
          'classes': ['collapse']
          }))

    def getUf(self, obj):
        return '%s' % (obj.casa_legislativa.municipio.uf)

    getUf.short_description = 'UF'

class EscolhaAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'schema', 'schema_to_open')
    raw_id_fields = ('schema', 'schema_to_open')
    ordering = ('schema', 'title')

class EscolhaInline(admin.TabularInline):
    model = Escolha
    fk_name = 'schema'
    raw_id_fields = ('schema_to_open',)
    verbose_name = 'Escolhas (apenas para choices ou multiple choices)'
    extra = 0

class PerguntaAdmin (BaseSchemaAdmin):
    search_fields = ('title', 'help_text', 'name',)
    list_display = ('title', 'categoria', 'datatype', 'help_text', 'required')
    list_filter = ('datatype', 'categoria', 'required')
    inlines = (EscolhaInline,)

admin.site.register(Diagnostico, DiagnosticoAdmin)
admin.site.register(Pergunta, PerguntaAdmin)
admin.site.register(Escolha, EscolhaAdmin)
admin.site.register(Anexo, AnexoAdmin)
admin.site.register(Categoria)
