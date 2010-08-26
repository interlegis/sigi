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

from sigi.apps.casas.views import casa_info, labels_report

class ContatosInline(generic.GenericTabularInline):
    model = Contato
    extra = 2
    raw_id_fields = ('municipio',)

class TelefonesInline(generic.GenericTabularInline):
    model = Telefone
    extra = 2

class ConveniosInline(admin.TabularInline):
    model = Convenio
    exclude = ['equipada','conveniada','observacao']
    extra = 1

class CasaLegislativaAdmin(admin.ModelAdmin):
    form = CasaLegislativaForm
    change_form_template = 'casas/change_form.html'
    change_list_template = 'casas/change_list.html'
    actions = ['etiqueta','relatorio','relatorio_completo']
    inlines = (TelefonesInline, ContatosInline, ConveniosInline)
    list_display = ('nome','municipio','presidente','logradouro')
    list_display_links = ('nome',)
    list_filter = ('tipo', 'municipio')
    ordering = ('nome','municipio__uf')
    fieldsets = (
        (None, {
            'fields': ('tipo', 'nome', 'telefone', 'cnpj',
                       'presidente'),
        }),
        ('Endereço', {
            'fields': ('logradouro', 'bairro', 'municipio', 'cep'),
        }),
        ('Outras informações', {
            'classes': ('collapse',),
            'fields': ('observacoes', 'email', 'pagina_web', 'foto'),
        }),
    )
    raw_id_fields = ('municipio',)
    search_fields = ('nome','cnpj', 'logradouro', 'bairro',
                     'cep', 'municipio__nome', 'municipio__uf__nome',
                     'municipio__codigo_ibge', 'pagina_web', 'observacoes')

    def changelist_view(self, request, extra_context=None):
        return super(CasaLegislativaAdmin, self).changelist_view(
            request,
            extra_context={'query_str': '?' + request.META['QUERY_STRING']}
        )

    def etiqueta(modelAdmin,request,queryset):
        response = HttpResponse(mimetype='application/pdf')        
        return labels_report(request,queryset=queryset)
    etiqueta.short_description = "Gerar etiqueta(s) da(s) casa(s) selecionada(s)"

    def relatorio(modelAdmin,request,queryset):
        response = HttpResponse(mimetype='application/pdf')
        report = CasasLegislativasReport(queryset=queryset)
        report.generate_by(PDFGenerator, filename=response)
        return response
    relatorio.short_description = u"Gerar relatório resumido da(s) casa(s) selecionada(s)"

    def relatorio_completo(modelAdmin,request,queryset):
        response = HttpResponse(mimetype='application/pdf')
        return casa_info(request,queryset=queryset)
    relatorio_completo.short_description = u"Gerar relatório completo da(s) casa(s) selecionada(s)"
    
    def get_actions(self, request):
        actions = super(CasaLegislativaAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(CasaLegislativa, CasaLegislativaAdmin)
