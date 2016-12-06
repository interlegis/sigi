# -*- coding: utf-8 -*-
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from geraldo.generators import PDFGenerator

from sigi.apps.convenios.models import (Anexo, Convenio, EquipamentoPrevisto,
                                        Projeto, Tramitacao)
from sigi.apps.convenios.reports import ConvenioReport
from sigi.apps.convenios.views import adicionar_convenios_carrinho
from sigi.apps.utils import queryset_ascii
from sigi.apps.utils.base_admin import BaseModelAdmin


class TramitacaoInline(admin.TabularInline):
    model = Tramitacao
    extra = 1


class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub', ]


class EquipamentoPrevistoInline(admin.TabularInline):
    model = EquipamentoPrevisto
    extra = 2
    raw_id_fields = ('equipamento',)


class AnexoAdmin(BaseModelAdmin):
    date_hierarchy = 'data_pub'
    exclude = ['data_pub', ]
    list_display = ('arquivo', 'descricao', 'data_pub', 'convenio')
    raw_id_fields = ('convenio',)
    search_fields = ('descricao', 'convenio__id', 'arquivo',
                     'convenio__casa_legislativa__nome')


class ConvenioAdmin(BaseModelAdmin):
    change_list_template = 'convenios/change_list.html'
    fieldsets = (
        (None,
            {'fields': ('casa_legislativa', 'num_processo_sf', 'num_convenio', 'projeto', 'observacao')}
         ),
        (_(u'Datas'),
            {'fields': ('data_adesao', 'data_retorno_assinatura',
                        'data_termo_aceite', 'data_pub_diario',
                        'data_devolucao_via', 'data_postagem_correio')}
         ),
        (_(u'Datas - Convenio sem assinatura'),
            {'fields': ('data_devolucao_sem_assinatura', 'data_retorno_sem_assinatura',)}
         ),
    )
    actions = ['adicionar_convenios']
    inlines = (TramitacaoInline, AnexosInline, EquipamentoPrevistoInline)
    list_display = ('num_convenio', 'casa_legislativa', 'get_uf',
                    'data_adesao', 'data_retorno_assinatura', 'data_pub_diario', 'data_termo_aceite',
                    'projeto',
                    )
    list_display_links = ('num_convenio', 'casa_legislativa',)
    list_filter = ('projeto', 'casa_legislativa__municipio__uf', 'casa_legislativa', 'conveniada', 'equipada')
    #date_hierarchy = 'data_adesao'
    ordering = ('casa_legislativa__tipo__sigla', 'casa_legislativa__municipio__uf', 'casa_legislativa')
    raw_id_fields = ('casa_legislativa',)
    get_queryset = queryset_ascii
    search_fields = ('id', 'search_text',  # 'casa_legislativa__nome',
                     'num_processo_sf', 'num_convenio')

    def get_uf(self, obj):
        return obj.casa_legislativa.municipio.uf.sigla
    get_uf.short_description = _(u'UF')
    get_uf.admin_order_field = 'casa_legislativa__municipio__uf__sigla'

    def changelist_view(self, request, extra_context=None):
        import re
        request.GET._mutable = True
        if 'data_retorno_assinatura__gte' in request.GET:
            value = request.GET.get('data_retorno_assinatura__gte', '')
            if value == '':
                del request.GET['data_retorno_assinatura__gte']
            elif re.match('^\d*$', value):  # Year only
                request.GET['data_retorno_assinatura__gte'] = "%s-01-01" % value  # Complete with january 1st
            elif re.match('^\d*\D\d*$', value):  # Year and month
                request.GET['data_retorno_assinatura__gte'] = '%s-01' % value  # Complete with 1st day of month
        if 'data_retorno_assinatura__lte' in request.GET:
            value = request.GET.get('data_retorno_assinatura__lte', '')
            if value == '':
                del request.GET['data_retorno_assinatura__lte']
            elif re.match('^\d*$', value):  # Year only
                request.GET['data_retorno_assinatura__lte'] = "%s-01-01" % value  # Complete with january 1st
            elif re.match('^\d*\D\d*$', value):  # Year and month
                request.GET['data_retorno_assinatura__lte'] = '%s-01' % value  # Complete with 1st day of month
        request.GET._mutable = False

        return super(ConvenioAdmin, self).changelist_view(
            request,
            extra_context={'query_str': '?' + request.META['QUERY_STRING']}
        )

    def relatorio(self, request, queryset):
        # queryset.order_by('casa_legislativa__municipio__uf')
        response = HttpResponse(content_type='application/pdf')
        report = ConvenioReport(queryset=queryset)
        report.generate_by(PDFGenerator, filename=response)
        return response
    relatorio.short_description = _(u'Exportar convênios selecionados para PDF')

    def adicionar_convenios(self, request, queryset):
        if 'carrinho_convenios' in request.session:
            q1 = len(request.session['carrinho_convenios'])
        else:
            q1 = 0
        adicionar_convenios_carrinho(request, queryset=queryset)
        q2 = len(request.session['carrinho_convenios'])
        quant = q2 - q1
        if quant:
            self.message_user(request, str(q2 - q1) + _(u" Convênios adicionados no carrinho"))
        else:
            self.message_user(request, _(u"Os Convênios selecionados já foram adicionadas anteriormente"))
        return HttpResponseRedirect('.')
    adicionar_convenios.short_description = _(u"Armazenar convênios no carrinho para exportar")

    def get_actions(self, request):
        actions = super(ConvenioAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def lookup_allowed(self, lookup, value):
        return super(ConvenioAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['casa_legislativa__municipio__uf__codigo_ibge__exact']


class EquipamentoPrevistoAdmin(BaseModelAdmin):
    list_display = ('convenio', 'equipamento', 'quantidade')
    list_display_links = ('convenio', 'equipamento')
    ordering = ('convenio', 'equipamento')
    raw_id_fields = ('convenio', 'equipamento')
    search_fields = ('convenio__id', 'equipamento__fabricante__nome',
                     'equipamento__modelo__modelo', 'equipamento__modelo__tipo__tipo')

admin.site.register(Projeto)
admin.site.register(Convenio, ConvenioAdmin)
admin.site.register(EquipamentoPrevisto, EquipamentoPrevistoAdmin)
