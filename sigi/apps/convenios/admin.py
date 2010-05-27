# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.convenios.models import Projeto, Convenio, EquipamentoPrevisto, Anexo
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.servicos.models import Servico
from django.http import HttpResponseRedirect

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
    actions = ['delete_selected', 'relatorio']
    inlines = (AnexosInline, EquipamentoPrevistoInline)
    list_display = ('id', 'casa_legislativa',
                    'num_processo_sf', 'data_adesao', 'projeto')
    list_filter  = ('projeto','casa_legislativa')
    date_hierarchy = 'data_adesao'                    
    ordering = ('-id',)
    raw_id_fields = ('casa_legislativa',)
    search_fields = ('id', 'casa_legislativa__nome',
                     'num_processo_sf')

    def changelist_view(self, request, extra_context=None):
        return super(ConvenioAdmin, self).changelist_view(
            request,
            extra_context={'query_str': '?' + request.META['QUERY_STRING']}
        )
    def relatorio(modeladmin, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        print selected
        return HttpResponseRedirect("reports/?ids=%s"%(",".join(selected)))
    relatorio.short_description = 'Selecione para gerar relatorio'
    

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
