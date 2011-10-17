# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes import generic
from sigi.apps.contatos.models import Contato
from sigi.apps.servicos.models import Servico
from sigi.apps.servicos.models import DominioLeg 

class ContatosInline(generic.GenericTabularInline):
    model = Contato
    extra = 2
    raw_id_fields = ('municipio',)
    verbose_name = 'colaborador Interlegis'
    verbose_name_plural = 'colaboradores Interlegis'

class ServicoAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_inicio'
    inlines = (ContatosInline,)
    list_display = ('id', 'titulo', 'tipo', 'convenio', 'situacao')
    list_filter  = ('tipo','situacao', 'avaliacao')
    raw_id_fields = ('convenio',)
    search_fields = ('titulo', 'tipo', 'descricao')
class DominiolegAdmin(admin.ModelAdmin):
    model = DominioLeg
    date_hierarchy = 'data_preenchimento'
    list_display = ('id', 'dominio', 'contato_administrativo', 'contato_tecnico', 'data_preenchimento', 'data_recebimento', 'data_atendimento',)
    search_fields = ('dominio',)
    
admin.site.register(DominioLeg, DominiolegAdmin)    
admin.site.register(Servico, ServicoAdmin)