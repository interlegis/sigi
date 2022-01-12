from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from sigi.apps.contatos.models import Contato, Telefone
from sigi.apps.inventario.models import (Fornecedor, Fabricante, Equipamento,
                                         TipoEquipamento, ModeloEquipamento,
                                         Bem)


class ContatosInline(GenericTabularInline):
    model = Contato
    extra = 2
    raw_id_fields = ('municipio',)

class TelefonesInline(GenericTabularInline):
    model = Telefone
    extra = 2

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    inlines = (TelefonesInline, ContatosInline)
    list_display = ('id', 'nome', 'email', 'pagina_web')
    list_display_links = ('id', 'nome')
    list_filter = ('nome',)
    search_fields = ('id', 'nome', 'email', 'pagina_web')

@admin.register(Fabricante)
class FabricanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    list_display_links = list_display
    list_filter = ('nome',)
    search_fields = ('id', 'nome')

@admin.register(TipoEquipamento)
class TipoEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')
    list_display_links = list_display
    list_filter = ('tipo',)
    search_fields = ('id', 'tipo')

@admin.register(ModeloEquipamento)
class ModeloEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'modelo')
    list_filter = ('tipo', 'modelo')
    ordering = ('tipo', 'modelo')
    search_fields = ('id', 'tipo', 'modelo')
    raw_id_fields = ('tipo',)

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fabricante', 'modelo', 'get_tipo')
    list_display_links = ('id',)
    list_filter = ('fabricante',)
    ordering = ('fabricante', 'modelo')
    raw_id_fields = ('fabricante', 'modelo')
    search_fields = ('id', 'modelo', 'fabricante')

    def get_tipo(self, obj):
        return obj.modelo.tipo.tipo
    get_tipo.short_description = 'tipo'

@admin.register(Bem)
class BemAdmin(admin.ModelAdmin):
    list_display = ('equipamento', 'fornecedor', 'num_serie',
                    'casa_legislativa')
    list_filter = ('fornecedor',)
    ordering = ('casa_legislativa', 'fornecedor', 'equipamento')
    raw_id_fields = ('casa_legislativa', 'equipamento', 'fornecedor')
    search_fields = ('fornecedor__nome', 'equipamento__fabricante__nome',
                     'equipamento__modelo__modelo', 'num_serie',
                     'num_tombamento', 'casa_legislativa__nome')
