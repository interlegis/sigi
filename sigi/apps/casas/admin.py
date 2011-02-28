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
from sigi.apps.casas.views import casa_info, labels_report, export_csv, \
                                    labels_report_sem_presidente, report
from sigi.apps.utils import queryset_ascii

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
    actions = ['etiqueta','relatorio','relatorio_csv','relatorio_completo','etiqueta_sem_presidente', 'adicionar_casas', 'teste']
    inlines = (TelefonesInline, ContatosInline, ConveniosInline)
    list_display = ('nome','municipio','presidente','logradouro')
    list_display_links = ('nome',)
    list_filter = ('tipo', 'municipio')
    ordering = ('nome','municipio__uf')
    queyrset = queryset_ascii
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
    search_fields = ('search_text','cnpj', 'bairro', 'logradouro',
                     'cep', 'municipio__nome', 'municipio__uf__nome',
                     'municipio__codigo_ibge', 'pagina_web', 'observacoes')

    def changelist_view(self, request, extra_context=None):
        return super(CasaLegislativaAdmin, self).changelist_view(
            request,
            extra_context={'query_str': '?' + request.META['QUERY_STRING']}
        )

    def etiqueta(modelAdmin,request,queryset):        
        return labels_report(request,queryset=queryset)
    etiqueta.short_description = "Gerar etiqueta(s) da(s) casa(s) selecionada(s)"

    def etiqueta_sem_presidente(modelAdmin,request,queryset):        
        return labels_report_sem_presidente(request,queryset=queryset)
    etiqueta_sem_presidente.short_description = "Gerar etiqueta(s) sem presidente da(s) casa(s) selecionada(s)"

    def relatorio(modelAdmin,request,queryset):        
        return report(request,queryset=queryset)
    relatorio.short_description = u"Exportar a(s) casa(s) selecionada(s) para PDF"

    def relatorio_completo(modelAdmin,request,queryset):        
        return casa_info(request,queryset=queryset)
    relatorio_completo.short_description = u"Gerar relatório completo da(s) casa(s) selecionada(s)"

    def relatorio_csv(modelAdmin,request,queryset):        
        return export_csv(request)        
    relatorio_csv.short_description = u"Exportar casa(s) selecionada(s) para CSV"
    
    def adicionar_casas(modelAdmin, request, queryset):
        if request.method == 'POST':
            ids_selecionados = request.POST.getlist('_selected_action')
            print "Selecionados atual :",
            print ids_selecionados
            if request.session.has_key('ids_selecionados_etiqueta') == False:
                request.session['ids_selecionados_etiqueta'] = ids_selecionados
            else:
                lista = request.session['ids_selecionados_etiqueta']
                print "Selecionados anteriormente :",
                print lista                
                lista.extend(ids_selecionados)
                print "Todos selecionados :",
                print lista
                request.session['ids_selecionados_etiqueta'] = lista
    
    def get_actions(self, request):
        actions = super(CasaLegislativaAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(CasaLegislativa, CasaLegislativaAdmin)
