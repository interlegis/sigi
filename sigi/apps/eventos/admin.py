from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from tinymce.models import HTMLField
from tinymce.widgets import AdminTinyMCE
from sigi.apps.eventos.models import (ModeloDeclaracao, Modulo, TipoEvento,
                                      Funcao, Evento, Equipe, Convite, Anexo)
from sigi.apps.eventos.forms import EventoAdminForm

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


class EquipeInline(admin.TabularInline):
    model = Equipe

class ConviteInline(admin.TabularInline):
    model = Convite
    raw_id_fields = ('casa',)

class ModuloInline(admin.TabularInline):
    model = Modulo

class AnexoInline(admin.TabularInline):
    model = Anexo
    exclude = ('data_pub',)

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    form = EventoAdminForm
    date_hierarchy = 'data_inicio'
    list_display = ('nome', 'tipo_evento', 'status', 'data_inicio',
                    'data_termino', 'municipio', 'solicitante',
                    'total_participantes',)
    list_filter = ('status', 'tipo_evento', 'tipo_evento__categoria', 'virtual',
                   'municipio__uf', 'solicitante')
    raw_id_fields = ('casa_anfitria', 'municipio',)
    search_fields = ('nome', 'tipo_evento__nome', 'casa_anfitria__search_text',
                     'municipio__search_text', 'solicitante')
    inlines = (EquipeInline, ConviteInline, ModuloInline, AnexoInline)

    def lookup_allowed(self, lookup, value):
        return (super(EventoAdmin, self).lookup_allowed(lookup, value) or
                lookup in ['tipo_evento__nome__exact',
                            'tipo_evento__nome__contains'])
