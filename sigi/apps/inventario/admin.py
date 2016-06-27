# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from sigi.apps.contatos.models import Contato, Telefone
from sigi.apps.inventario.models import (Bem, Equipamento, Fabricante,
                                         Fornecedor, ModeloEquipamento,
                                         TipoEquipamento)
from sigi.apps.utils.base_admin import BaseModelAdmin


class ContatosInline(GenericTabularInline):
    model = Contato
    extra = 2
    raw_id_fields = ('municipio',)


class TelefonesInline(GenericTabularInline):
    model = Telefone
    extra = 2


class FornecedorAdmin(BaseModelAdmin):
    inlines = (TelefonesInline, ContatosInline)
    list_display = ('id', 'nome', 'email', 'pagina_web')
    list_display_links = ('id', 'nome')
    list_filter = ('nome',)
    search_fields = ('id', 'nome', 'email', 'pagina_web')


class FabricanteAdmin(BaseModelAdmin):
    list_display = ('id', 'nome')
    list_display_links = list_display
    list_filter = ('nome',)
    search_fields = ('id', 'nome')


class TipoEquipamentoAdmin(BaseModelAdmin):
    list_display = ('id', 'tipo')
    list_display_links = list_display
    list_filter = ('tipo',)
    search_fields = ('id', 'tipo')


class ModeloEquipamentoAdmin(BaseModelAdmin):
    list_display = ('id', 'tipo', 'modelo')
    list_filter = ('tipo', 'modelo')
    ordering = ('tipo', 'modelo')
    search_fields = ('id', 'tipo', 'modelo')
    raw_id_fields = ('tipo',)


class EquipamentoAdmin(BaseModelAdmin):
    list_display = ('id', 'fabricante', 'modelo', 'get_tipo')
    list_display_links = ('id',)
    list_filter = ('fabricante',)
    ordering = ('fabricante', 'modelo')
    raw_id_fields = ('fabricante', 'modelo')
    search_fields = ('id', 'modelo', 'fabricante')

    def get_tipo(self, obj):
        return obj.modelo.tipo.tipo
    get_tipo.short_description = 'tipo'


class BemAdmin(BaseModelAdmin):
    list_display = ('equipamento', 'fornecedor', 'num_serie',
                    'casa_legislativa')
    list_filter = ('fornecedor',)
    ordering = ('casa_legislativa', 'fornecedor', 'equipamento')
    raw_id_fields = ('casa_legislativa', 'equipamento', 'fornecedor')
    search_fields = ('fornecedor__nome', 'equipamento__fabricante__nome',
                     'equipamento__modelo__modelo', 'num_serie',
                     'num_tombamento', 'casa_legislativa__nome')

admin.site.register(Fornecedor, FornecedorAdmin)
admin.site.register(Fabricante, FabricanteAdmin)
admin.site.register(TipoEquipamento, TipoEquipamentoAdmin)
admin.site.register(ModeloEquipamento, ModeloEquipamentoAdmin)
admin.site.register(Equipamento, EquipamentoAdmin)
admin.site.register(Bem, BemAdmin)
