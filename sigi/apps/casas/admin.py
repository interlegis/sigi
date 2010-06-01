# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from sigi.apps.casas.forms import CasaLegislativaForm
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import Contato, Telefone
from sigi.apps.convenios.models import Projeto, Convenio, EquipamentoPrevisto, Anexo

class ContatosInline(generic.GenericTabularInline):
    model = Contato
    extra = 2
    raw_id_fields = ('municipio',)

class TelefonesInline(generic.GenericTabularInline):
    model = Telefone
    extra = 2

class ConveniosInline(admin.TabularInline):
    model = Convenio
    extra = 1

class CasaLegislativaAdmin(admin.ModelAdmin):
    form = CasaLegislativaForm
    change_form_template = 'casas/change_form.html'
    change_list_template = 'casas/change_list.html'
    inlines = (TelefonesInline, ContatosInline, ConveniosInline)
    list_display = ('nome', 'email', 'pagina_web', 'municipio')
    list_display_links = ('nome',)
    list_filter = ('tipo', 'municipio')
    fieldsets = (
        (None, {
            'fields': ('nome', 'sigla', 'tipo', 'cnpj', 'observacoes',
                       'parlamentar'),
        }),
        ('Endereço', {
            'fields': ('logradouro', 'bairro', 'municipio', 'cep'),
        }),
        ('Outras informações', {
            'classes': ('collapse',),
            'fields': ('email', 'pagina_web', 'foto', 'historico'),
        }),
    )
    raw_id_fields = ('municipio','parlamentar')
    search_fields = ('nome', 'sigla', 'cnpj', 'logradouro', 'bairro',
                     'cep', 'municipio__nome', 'municipio__uf__nome',
                     'municipio__codigo_ibge', 'pagina_web', 'observacoes')

    def changelist_view(self, request, extra_context=None):
        return super(CasaLegislativaAdmin, self).changelist_view(
            request,
            extra_context={'query_str': '?' + request.META['QUERY_STRING']}
        )

admin.site.register(CasaLegislativa, CasaLegislativaAdmin)
