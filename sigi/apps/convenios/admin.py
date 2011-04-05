# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.convenios.models import Projeto, Convenio, EquipamentoPrevisto, Anexo
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.servicos.models import Servico
from django.http import HttpResponse, HttpResponseRedirect
from sigi.apps.convenios.reports import ConvenioReport
from sigi.apps.utils import queryset_ascii
from geraldo.generators import PDFGenerator

from sigi.apps.convenios.views import adicionar_convenios_carrinho

class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub',]

class EquipamentoPrevistoInline(admin.TabularInline):
    model = EquipamentoPrevisto
    extra = 2
    raw_id_fields = ('equipamento',)

class AnexoAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_pub'
    exclude = ['data_pub',]
    list_display = ('arquivo', 'descricao', 'data_pub', 'convenio')
    raw_id_fields = ('convenio',)
    search_fields = ('descricao', 'convenio__id', 'arquivo',
                     'convenio__casa_legislativa__nome')

class ConvenioAdmin(admin.ModelAdmin):
    change_list_template = 'convenios/change_list.html'
    fieldsets = (
        (None,
            {'fields': ('casa_legislativa', 'num_processo_sf','num_convenio','projeto','observacao')}
        ),
        ('Datas',
            {'fields': ('data_adesao', 'data_retorno_assinatura',
                        'data_termo_aceite', 'data_pub_diario',
                        'data_devolucao_via', 'data_postagem_correio')}
        ),
    )
    actions = ['adicionar_convenios']
    inlines = (AnexosInline, EquipamentoPrevistoInline)
    list_display = ('num_convenio', 'casa_legislativa',
                    'data_adesao','data_retorno_assinatura','data_termo_aceite',
                    'projeto',
                    )
    list_display_links = ('num_convenio','casa_legislativa',)
    list_filter  = ('projeto','casa_legislativa','conveniada', 'equipada')
    #date_hierarchy = 'data_adesao'
    ordering = ('casa_legislativa__tipo__sigla','casa_legislativa__municipio__uf','casa_legislativa')
    raw_id_fields = ('casa_legislativa',)
    queryset = queryset_ascii
    search_fields = ('id', 'search_text',#'casa_legislativa__nome',
                     'num_processo_sf','num_convenio')

    def changelist_view(self, request, extra_context=None):
        return super(ConvenioAdmin, self).changelist_view(
            request,
            extra_context={'query_str': '?' + request.META['QUERY_STRING']}
        )
    def relatorio(self, request, queryset):
        #queryset.order_by('casa_legislativa__municipio__uf')        
        response = HttpResponse(mimetype='application/pdf')
        report = ConvenioReport(queryset=queryset)
        report.generate_by(PDFGenerator, filename=response)
        return response                
    relatorio.short_description = u'Exportar convênios selecionados para PDF'
    
    def adicionar_convenios(self, request, queryset):        
        if request.session.has_key('carrinho_convenios'):
            q1 = len(request.session['carrinho_convenios'])
        else:
            q1 = 0        
        adicionar_convenios_carrinho(request,queryset=queryset)
        q2 = len(request.session['carrinho_convenios'])
        quant = q2 - q1
        if quant:
            self.message_user(request,str(q2-q1)+" Convênios adicionados no carrinho" )
        else:
            self.message_user(request,"Os Convênios selecionados já foram adicionadas anteriormente" )
        return HttpResponseRedirect('.')
    adicionar_convenios.short_description = u"Armazenar convênios no carrinho para exportar"
    
    def get_actions(self, request):
        actions = super(ConvenioAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
    

class EquipamentoPrevistoAdmin(admin.ModelAdmin):
    list_display = ('convenio', 'equipamento', 'quantidade')
    list_display_links = ('convenio', 'equipamento')
    ordering = ('convenio', 'equipamento')
    raw_id_fields = ('convenio', 'equipamento')
    search_fields = ('convenio__id', 'equipamento__fabricante__nome',
                     'equipamento__modelo__modelo', 'equipamento__modelo__tipo__tipo')

#admin.site.register(Projeto)
admin.site.register(Convenio, ConvenioAdmin)
#admin.site.register(CasaLegislativa)
admin.site.register(EquipamentoPrevisto, EquipamentoPrevistoAdmin)
