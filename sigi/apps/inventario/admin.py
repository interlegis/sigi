# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.inventario.models import (Fornecedor, Fabricante, Equipamento,
                                         TipoEquipamento, ModeloEquipamento,
                                         Bem)

class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')

class FabricanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')

class TipoEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')

class ModeloEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'modelo')

class EquipamentoAdmin(admin.ModelAdmin):
    ordering = ('fabricante', 'modelo')
    list_display = ('id', 'modelo', 'fabricante')
    list_filter  = ('fabricante',)

class BemAdmin(admin.ModelAdmin):
    ordering = ('casa_legislativa', 'fornecedor', 'equipamento')
    list_display = ('equipamento', 'fornecedor', 'num_serie',
                    'num_tombamento', 'casa_legislativa')

admin.site.register(Fornecedor, FornecedorAdmin)
admin.site.register(Fabricante, FabricanteAdmin)
admin.site.register(TipoEquipamento, TipoEquipamentoAdmin)
admin.site.register(ModeloEquipamento,ModeloEquipamentoAdmin)
admin.site.register(Equipamento, EquipamentoAdmin)
admin.site.register(Bem, BemAdmin)
