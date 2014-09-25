# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

from filters import OcorrenciaListFilter
from sigi.apps.ocorrencias.models import Ocorrencia, Comentario, Anexo, Categoria, TipoContato
from sigi.apps.servidores.models import Servidor


class ComentarioViewInline(admin.TabularInline):
    model = Comentario
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name, verbose_name_plural = u"Comentário anterior", u"Comentários anteriores"
    fields = ('usuario', 'data_criacao', 'novo_status', 'encaminhar_setor', 'descricao', )
    readonly_fields = ('novo_status', 'encaminhar_setor', 'descricao', 'data_criacao', 'usuario',)


class ComentarioInline(admin.StackedInline):
    model = Comentario
    extra = 1
    verbose_name, verbose_name_plural = u"Comentário novo", u"Comentários novos"
    fieldsets = ((None, {'fields': (('novo_status', 'encaminhar_setor',), 'descricao', )}),)

    def get_queryset(self, queryset):
        return self.model.objects.get_query_set()


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
        qs = super(OcorrenciaChangeList, self).get_query_set(request)
        self.params = tmp_params.copy()
        if grupo:
            servidor = Servidor.objects.get(user=self.request.user)
            if grupo == 'S':  # Apenas do meu setor
                qs = qs.filter(setor_responsavel=servidor.servico)
            elif grupo == 'M':  # Apenas criados por mim
                qs = qs.filter(servidor_registro=servidor)
        return qs

class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('data_criacao', 'casa_legislativa', 'assunto', 'prioridade', 'status', 'data_modificacao', 'setor_responsavel',)
    list_filter = (OcorrenciaListFilter, 'status', 'prioridade', 'categoria__nome', 'setor_responsavel__nome', )
    search_fields = ('casa_legislativa__search_text', 'assunto', 'servidor_registro__nome_completo', )
    date_hierarchy = 'data_criacao'
    fields = ('casa_legislativa', 'categoria', 'tipo_contato', 'assunto', 'status', 'prioridade', 'descricao', 'servidor_registro',
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
            if obj.status in [3, 4, 5]:  # Fechados
                fields.append('prioridade')
        return fields

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            self.fields = ('casa_legislativa', 'categoria', 'tipo_contato', 'assunto', 'prioridade', 'descricao', 'resolucao', )
        else:
            self.fields = ('casa_legislativa', 'categoria', 'tipo_contato', 'assunto', 'status', 'prioridade', 'descricao',
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
                if instance.encaminhar_setor and (instance.encaminhar_setor != instance.ocorrencia.setor_responsavel):
                    instance.ocorrencia.setor_responsavel = instance.encaminhar_setor
                    instance.ocorrencia.save()
                if instance.novo_status and (instance.novo_status != instance.ocorrencia.status):
                    instance.ocorrencia.status = instance.novo_status
                    instance.ocorrencia.save()
            instance.save()
        super(OcorrenciaAdmin, self).save_formset(request, form, formset, change)


admin.site.register(Ocorrencia, OcorrenciaAdmin)
admin.site.register(Categoria)
admin.site.register(TipoContato)
