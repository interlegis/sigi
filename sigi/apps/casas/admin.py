# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.filterspecs import ChoicesFilterSpec, FilterSpec
from django.contrib.contenttypes import generic
from sigi.apps.casas.forms import CasaLegislativaForm
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import Contato
from sigi.apps.contatos.models import Telefone

class ContatosInline(generic.GenericTabularInline):
    model = Contato

class TelefonesInline(generic.GenericTabularInline):
    model = Telefone

class CasaLegislativaAdmin(admin.ModelAdmin):
    form = CasaLegislativaForm
    inlines = (TelefonesInline, ContatosInline)
    list_display = ('nome', 'email', 'pagina_web', 'municipio', 'uf')
    list_display_links = ('nome',)
    list_filter = ('tipo',)
    fieldsets = (
        (None, {
            'fields': ('nome', 'sigla', 'tipo', 'cnpj'),
        }),
        ('Endereço', {
            'fields': ('logradouro', 'bairro', 'municipio', 'cep'),
        }),
        ('Outras informações', {
            'fields': ('email', 'pagina_web', 'foto', 'historico'),
        }),
    )
    search_fields = ('nome', 'sigla', 'cnpj', 'logradouro', 'bairro',
                     'cep', 'municipio__nome', 'municipio__uf__nome',
                     'pagina_web')

admin.site.register(CasaLegislativa, CasaLegislativaAdmin)
