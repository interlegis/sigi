from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from import_export.fields import Field
from tinymce.models import HTMLField
from tinymce.widgets import AdminTinyMCE
from sigi.apps.eventos.models import (ModeloDeclaracao, Modulo, TipoEvento,
                                      Funcao, Evento, Equipe, Convite, Anexo)
from sigi.apps.eventos.forms import EventoAdminForm
from sigi.apps.utils.filters import EmptyFilter
from sigi.apps.utils.mixins import CartExportMixin, ValueLabeledResource

class EventoResource(ValueLabeledResource):
    # categoria_evento = Field(column_name="tipo_evento__categoria")
    # status = Field(column_name="status")
    class Meta:
        model = Evento
        fields = (
            'id', 'tipo_evento__nome', 'tipo_evento__categoria', 'nome',
            'descricao', 'virtual', 'solicitante', 'num_processo',
            'data_pedido', 'data_inicio', 'data_termino', 'carga_horaria',
            'casa_anfitria__nome', 'casa_anfitria__logradouro',
            'casa_anfitria__bairro', 'casa_anfitria__municipio__nome',
            'casa_anfitria__municipio__uf__sigla', 'casa_anfitria__cep',
            'casa_anfitria__email', 'local', 'municipio__nome',
            'municipio__uf__sigla', 'observacao', 'publico_alvo',
            'total_participantes', 'status', 'data_cancelamento',
            'motivo_cancelamento', 'equipe__membro__nome_completo',
            'equipe__funcao__nome', 'convite__casa__nome',
            'convite__casa__municipio__nome',
            'convite__casa__municipio__uf__sigla', 'convite__casa__cep',
            'convite__casa__email', 'convite__aceite', 'convite__data_convite',
            'convite__participou', 'convite__qtde_participantes',
            'convite__nomes_participantes',
        )
        export_order = fields

    def dehydrate_tipo_evento__categoria(self, obj):
        return dict(TipoEvento.CATEGORIA_CHOICES)[obj['tipo_evento__categoria']]

    def dehydrate_virtual(self, obj):
        return "Sim" if obj['virtual'] else "Não"

    def dehydrate_status(self, obj):
        return dict(Evento.STATUS_CHOICES)[obj['status']]

    def dehydrate_convite__aceite(self, obj):
        return "Sim" if obj['convite__aceite'] else "Não"

    def dehydrate_convite__participou(self, obj):
        return "Sim" if obj['convite__participou'] else "Não"

@admin.register(TipoEvento)
class TipoEventAdmin(admin.ModelAdmin):
    search_fields = ('nome',)

@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao',)
    search_fields = ('nome', 'descricao',)

@admin.register(ModeloDeclaracao)
class ModeloDeclaracaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'formato')
    formfield_overrides = {HTMLField: {'widget': AdminTinyMCE}}

class EquipeInline(admin.StackedInline):
    model = Equipe

class ConviteInline(admin.StackedInline):
    model = Convite
    raw_id_fields = ('casa',)

class ModuloInline(admin.StackedInline):
    model = Modulo

class AnexoInline(admin.StackedInline):
    model = Anexo
    exclude = ('data_pub',)

@admin.register(Evento)
class EventoAdmin(CartExportMixin, admin.ModelAdmin):
    form = EventoAdminForm
    resource_class = EventoResource
    date_hierarchy = 'data_inicio'
    list_display = ('nome', 'tipo_evento', 'status', 'link_sigad',
                    'data_inicio', 'data_termino', 'municipio', 'solicitante',
                    'total_participantes',)
    list_filter = ('status', ('num_processo', EmptyFilter), 'tipo_evento',
                   'tipo_evento__categoria', 'virtual', 'municipio__uf',
                   'solicitante')
    raw_id_fields = ('casa_anfitria', 'municipio',)
    search_fields = ('nome', 'tipo_evento__nome', 'casa_anfitria__search_text',
                     'municipio__search_text', 'solicitante')
    inlines = (EquipeInline, ConviteInline, ModuloInline, AnexoInline)
    save_as = True

    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return obj.get_sigad_url()
    link_sigad.short_description = _(u"número do processo SIGAD")
    link_sigad.allow_tags = True

    def lookup_allowed(self, lookup, value):
        return (super(EventoAdmin, self).lookup_allowed(lookup, value) or
                lookup in ['tipo_evento__nome__exact',
                            'tipo_evento__nome__contains'])
