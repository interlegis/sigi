# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from sigi.apps.casas.forms import CasaLegislativaForm
from sigi.apps.casas.models import CasaLegislativa, Presidente, Funcionario
from sigi.apps.contatos.models import Telefone
from sigi.apps.convenios.models import Projeto, Convenio, EquipamentoPrevisto, Anexo
from django.http import HttpResponse, HttpResponseRedirect
from sigi.apps.casas.reports import CasasLegislativasLabels, CasasLegislativasReport
from geraldo.generators import PDFGenerator
from sigi.apps.casas.views import report_complete, labels_report, export_csv, \
                                    labels_report_sem_presidente, report, \
                                    adicionar_casas_carrinho
from sigi.apps.utils import queryset_ascii

class TelefonesInline(generic.GenericTabularInline):
    model = Telefone
    readonly_fields = ('ult_alteracao',)
    extra = 1

class PresidenteInline(admin.StackedInline):
    model = Presidente
    exclude = ['cargo','funcao']
    readonly_fields = ('ult_alteracao',)
    extra = 1
    max_num = 1
    inlines = (TelefonesInline)

class FuncionariosInline(admin.StackedInline):
    model = Funcionario
    fieldsets = ((None, {
                    'fields': (('nome', 'sexo', 'nota', 'email'), ('cargo', 'funcao', 'setor', 'tempo_de_servico'), 'ult_alteracao') 
                }),)
    readonly_fields = ('ult_alteracao',)
    extra = 1
    inlines = (TelefonesInline,)
    def queryset(self, request):
        return self.model.objects.exclude(cargo="Presidente")

class ConveniosInline(admin.TabularInline):
    model = Convenio
    exclude = ['equipada','conveniada','observacao']
    extra = 1

class CasaLegislativaAdmin(admin.ModelAdmin):
    form = CasaLegislativaForm
    change_form_template = 'casas/change_form.html'
    change_list_template = 'casas/change_list.html'
    actions = ['adicionar_casas',]
    inlines = (TelefonesInline, PresidenteInline, FuncionariosInline, ConveniosInline)
    readonly_fields = ('ult_alt_endereco',)
    list_display = ('nome','municipio','logradouro', 'ult_alt_endereco')
    list_display_links = ('nome',)
    list_filter = ('tipo', 'municipio')
    ordering = ('nome','municipio__uf')
    queyrset = queryset_ascii
    fieldsets = (
        (None, {
            'fields': ('tipo', 'nome', 'cnpj', 'num_parlamentares')
        }),
        ('Endereço', {
            'fields': ('data_instalacao', 'logradouro', 'bairro',
                       'municipio', 'cep', 'pagina_web','email', 'ult_alt_endereco'),
        }),
        ('Outras informações', {
            'classes': ('collapse',),
            'fields': ('observacoes', 'foto'),
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

    def etiqueta(self,request,queryset):        
        return labels_report(request,queryset=queryset)
    etiqueta.short_description = "Gerar etiqueta(s) da(s) casa(s) selecionada(s)"

    def etiqueta_sem_presidente(self,request,queryset):        
        return labels_report_sem_presidente(request,queryset=queryset)
    etiqueta_sem_presidente.short_description = "Gerar etiqueta(s) sem presidente da(s) casa(s) selecionada(s)"

    def relatorio(self,request,queryset):        
        return report(request,queryset=queryset)
    relatorio.short_description = u"Exportar a(s) casa(s) selecionada(s) para PDF"

    def relatorio_completo(self,request,queryset):        
        return report_complete(request,queryset=queryset)
    relatorio_completo.short_description = u"Gerar relatório completo da(s) casa(s) selecionada(s)"

    def relatorio_csv(self,request,queryset):        
        return export_csv(request)        
    relatorio_csv.short_description = u"Exportar casa(s) selecionada(s) para CSV"
    
    def adicionar_casas(self, request, queryset):        
        if request.session.has_key('carrinho_casas'):
            q1 = len(request.session['carrinho_casas'])
        else:
            q1 = 0        
        response = adicionar_casas_carrinho(request,queryset=queryset)
        q2 = len(request.session['carrinho_casas'])
        quant = q2 - q1
        if quant:
            self.message_user(request,str(q2-q1)+" Casas Legislativas adicionadas no carrinho" )
        else:
            self.message_user(request,"As Casas Legislativas selecionadas já foram adicionadas anteriormente" )
        return HttpResponseRedirect('.')
    
    adicionar_casas.short_description = u"Armazenar casas no carrinho para exportar"
        
    
    def get_actions(self, request):
        actions = super(CasaLegislativaAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(CasaLegislativa, CasaLegislativaAdmin)
