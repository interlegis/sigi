# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.utils.translation import ugettext as _

from filters import OcorrenciaListFilter
from sigi.apps.ocorrencias.models import (Anexo, Categoria, Comentario,
                                          Ocorrencia, TipoContato)
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils.base_admin import BaseModelAdmin


class ComentarioViewInline(admin.TabularInline):
    model = Comentario
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name, verbose_name_plural = _(u"Comentário anterior"), _(u"Comentários anteriores")
    fields = ('usuario', 'data_criacao', 'novo_status', 'encaminhar_setor', 'descricao', )
    readonly_fields = ('novo_status', 'encaminhar_setor', 'descricao', 'data_criacao', 'usuario',)


class ComentarioInline(admin.StackedInline):
    model = Comentario
    extra = 1
    verbose_name, verbose_name_plural = _(u"Comentário novo"), _(u"Comentários novos")
    fieldsets = ((None, {'fields': (('novo_status', 'encaminhar_setor',), 'descricao', )}),)

    def get_queryset(self, queryset):
        return self.model.objects.none()


class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    readonly_fields = ['data_pub', ]


class OcorrenciaChangeList(ChangeList):
    request = None

    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields,
                 list_select_related, list_per_page, list_max_show_all, list_editable, model_admin):
        self.request = request
        super(OcorrenciaChangeList, self).__init__(request, model, list_display, list_display_links, list_filter,
                                                   date_hierarchy, search_fields, list_select_related, list_per_page,
                                                   list_max_show_all, list_editable, model_admin)

    def get_queryset(self, request):
        tmp_params = self.params.copy()
        grupo = None
        if 'grupo' in self.params:
            grupo = self.params['grupo']
            del self.params['grupo']
        qs = super(OcorrenciaChangeList, self).get_queryset(request)
        self.params = tmp_params.copy()
        if grupo:
            servidor = Servidor.objects.get(user=self.request.user)
            if grupo == 'S':  # Apenas do meu setor
                qs = qs.filter(setor_responsavel=servidor.servico)
            elif grupo == 'M':  # Apenas criados por mim
                qs = qs.filter(servidor_registro=servidor)
        return qs


class OcorrenciaAdmin(BaseModelAdmin):
    list_display = ('data_criacao', 'casa_legislativa', 'get_municipio', 'get_uf', 'assunto', 'prioridade', 'status', 'data_modificacao', 'setor_responsavel',)
    list_filter = (OcorrenciaListFilter, 'status', 'prioridade', 'categoria__nome', 'setor_responsavel__nome', 'casa_legislativa__gerente_contas',)
    search_fields = ('casa_legislativa__search_text', 'assunto', 'servidor_registro__nome_completo', 'descricao', 'resolucao', 'ticket',)
    date_hierarchy = 'data_criacao'
    fields = ('casa_legislativa', 'categoria', 'tipo_contato', 'assunto', 'status', 'prioridade', 'ticket', 'descricao', 'servidor_registro',
              'setor_responsavel', 'resolucao', )
    readonly_fields = ('servidor_registro', 'setor_responsavel', )
    inlines = (ComentarioViewInline, ComentarioInline, AnexosInline, )
    raw_id_fields = ('casa_legislativa', )

    def get_changelist(self, request, **kwargs):
        return OcorrenciaChangeList

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj is not None:
            fields.extend(['casa_legislativa', 'categoria', 'tipo_contato', 'assunto', 'status', 'descricao', ])
            if obj.status in [Ocorrencia.STATUS_RESOLVIDO, Ocorrencia.STATUS_FECHADO, Ocorrencia.STATUS_DUPLICADO]:  # Fechados
                fields.append('prioridade')
        return fields

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            self.fields = ('casa_legislativa', 'categoria', 'tipo_contato', 'assunto', 'prioridade', 'ticket', 'descricao', 'resolucao', )
        else:
            self.fields = ('casa_legislativa', 'categoria', 'tipo_contato', 'assunto', 'status', 'prioridade', 'ticket', 'descricao',
                           'servidor_registro', 'setor_responsavel', 'resolucao', )

        return super(OcorrenciaAdmin, self).get_fieldsets(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.servidor_registro = Servidor.objects.get(user=request.user)
            obj.setor_responsavel = obj.categoria.setor_responsavel
        obj.save()

    def save_formset(self, request, form, formset, change):
        servidor = Servidor.objects.get(user=request.user)
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Comentario):
                instance.usuario = servidor
            instance.save()
        super(OcorrenciaAdmin, self).save_formset(request, form, formset, change)

    def get_uf(self, obj):
        return obj.casa_legislativa.municipio.uf
    get_uf.short_description = _(u'UF')
    get_uf.admin_order_field = 'casa_legislativa__municipio__uf'

    def get_municipio(self, obj):
        return obj.casa_legislativa.municipio.nome
    get_municipio.short_description = _(u'Município')
    get_municipio.admin_order_field = 'casa_legislativa__municipio__nome'


admin.site.register(Ocorrencia, OcorrenciaAdmin)
admin.site.register(Categoria)
admin.site.register(TipoContato)
