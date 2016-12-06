# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib import admin
from django.db.utils import OperationalError, ProgrammingError
from django.utils.translation import ugettext as _
from eav.admin import BaseEntityAdmin, BaseSchemaAdmin

from sigi.apps.diagnosticos.forms import DiagnosticoForm
from sigi.apps.diagnosticos.models import (Anexo, Categoria, Diagnostico,
                                           Equipe, Escolha, Pergunta)
from sigi.apps.utils.base_admin import BaseModelAdmin


def publicar_diagnostico(self, request, queryset):
    for registro in queryset:
        diagnostico = Diagnostico.objects.get(pk=registro.id)
        diagnostico.publicado = True
        diagnostico.data_publicacao = datetime.now()
        diagnostico.save()

        # Enviando o email avisando que o diagnóstico foi publicado
        email = diagnostico.responsavel.user.email
        if email:
            diagnostico.email_diagnostico_publicado(email, request.get_host())
    self.message_user(request, _(u"Diagnóstico(s) publicado(s) com sucesso!"))
publicar_diagnostico.short_description = _(u"""
    Definir diagnósticos como publicado""")


def despublicar_diagnostico(self, request, queryset):
    queryset.update(publicado=False)
despublicar_diagnostico.short_description = _(u"""
    Definir diagnósticos como não publicado""")


class EquipeInline(admin.TabularInline):
    model = Equipe


class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub', ]


class AnexoAdmin(BaseModelAdmin):
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
    list_display = ('casa_legislativa', 'get_uf', 'data_visita_inicio', 'data_visita_fim', 'responsavel', 'publicado')
    list_filter = ('publicado', 'casa_legislativa__municipio__uf__nome', 'casa_legislativa', 'data_publicacao', 'data_visita_inicio', 'data_visita_fim')
    raw_id_fields = ('casa_legislativa',)
    ordering = ('casa_legislativa',)

    eav_fieldsets = (
        (u'00. Identificação do Diagnóstico', {'fields': ('responsavel', 'data_visita_inicio', 'data_visita_fim',)}),
        (u'01. Identificação da Casa Legislativa', {'fields': ('casa_legislativa',)}),
        (u'02. Identificação de Competências da Casa Legislativa', {'fields': ()})
    )

    # popula o eav fieldsets ordenando as categorias e as perguntas
    # para serem exibidas no admin
    try:
        for categoria in Categoria.objects.all():
            # ordena as perguntas pelo title e utiliza o name no fieldset
            perguntas_by_title = [(p.title, p.name) for p in categoria.perguntas.all()]
            perguntas = [pergunta[1] for pergunta in sorted(perguntas_by_title)]

            eav_fieldsets += ((categoria, {
                'fields': tuple(perguntas),
                'classes': ['collapse']
            }),)
    except OperationalError:
        pass  # Hack to prevent Django.db.OperationalError on migrate/syncdb at creating new database
    except ProgrammingError:
        pass  # Hack to prevent Django.db.OperationalError on migrate/syncdb at creating new database

    def get_uf(self, obj):
        return '%s' % (obj.casa_legislativa.municipio.uf)
    get_uf.short_description = _(u'UF')
    get_uf.admin_order_field = 'casa_legislativa__municipio__uf__nome'

    def lookup_allowed(self, lookup, value):
        return super(DiagnosticoAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['casa_legislativa__municipio__uf__codigo_ibge__exact']

    def changelist_view(self, request, extra_context=None):
        import re
        request.GET._mutable = True
        if 'data_visita_inicio__gte' in request.GET:
            value = request.GET.get('data_visita_inicio__gte', '')
            if value == '':
                del request.GET['data_visita_inicio__gte']
            elif re.match('^\d*$', value):  # Year only
                request.GET['data_visita_inicio__gte'] = "%s-01-01" % value  # Complete with january 1st
            elif re.match('^\d*\D\d*$', value):  # Year and month
                request.GET['data_visita_inicio__gte'] = '%s-01' % value  # Complete with 1st day of month
        if 'data_visita_inicio__lte' in request.GET:
            value = request.GET.get('data_visita_inicio__lte', '')
            if value == '':
                del request.GET['data_visita_inicio__lte']
            elif re.match('^\d*$', value):  # Year only
                request.GET['data_visita_inicio__lte'] = "%s-01-01" % value  # Complete with january 1st
            elif re.match('^\d*\D\d*$', value):  # Year and month
                request.GET['data_visita_inicio__lte'] = '%s-01' % value  # Complete with 1st day of month
        request.GET._mutable = False

        return super(DiagnosticoAdmin, self).changelist_view(request, extra_context)


class EscolhaAdmin(BaseModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'schema', 'schema_to_open')
    raw_id_fields = ('schema', 'schema_to_open')
    ordering = ('schema', 'title')


class EscolhaInline(admin.TabularInline):
    model = Escolha
    fk_name = 'schema'
    raw_id_fields = ('schema_to_open',)
    verbose_name = _(u'Escolhas (apenas para choices ou multiple choices)')
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
