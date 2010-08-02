# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from sigi.apps.casas.forms import CasaLegislativaForm
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import Contato, Telefone
from sigi.apps.convenios.models import Projeto, Convenio, EquipamentoPrevisto, Anexo
from django.http import HttpResponse, HttpResponseRedirect
from sigi.apps.casas.reports import CasasLegislativasLabels, CasasLegislativasReport
from geraldo.generators import PDFGenerator

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
    actions = ['delete_selected','etiqueta','relatorio']
    inlines = (TelefonesInline, ContatosInline, ConveniosInline)
    list_display = ('nome','municipio','parlamentar','logradouro')
    list_display_links = ('nome',)
    list_filter = ('tipo', 'municipio')
    ordering = ('municipio__uf','nome')
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

    def etiqueta(modelAdmin,request,queryset):
        response = HttpResponse(mimetype='application/pdf')
        report = CasasLegislativasLabels(queryset=queryset)
        report.generate_by(PDFGenerator, filename=response)
        return response        
    etiqueta.short_description = "Gerar etiqueta(s) da(s) casa(s) selecionada(s)"

    def relatorio(modelAdmin,request,queryset):
        response = HttpResponse(mimetype='application/pdf')
        report = CasasLegislativasReport(queryset=queryset)
        report.generate_by(PDFGenerator, filename=response)
        return response
    relatorio.short_description = u"Gerar relatório(s) da(s) casa(s) selecionada(s)"

admin.site.register(CasaLegislativa, CasaLegislativaAdmin)
