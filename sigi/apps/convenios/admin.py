# -*- coding: utf-8 -*-
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from geraldo.generators import PDFGenerator

from sigi.apps.convenios.models import (Projeto, StatusConvenio,
                                        TipoSolicitacao, Convenio,
                                        EquipamentoPrevisto, Anexo, Tramitacao)
from sigi.apps.convenios.reports import ConvenioReport
from sigi.apps.convenios.views import adicionar_convenios_carrinho
from sigi.apps.utils import queryset_ascii
from sigi.apps.utils.base_admin import BaseModelAdmin
from sigi.apps.servidores.models import Servidor
from sigi.apps.casas.admin import GerentesInterlegisFilter

# class TramitacaoInline(admin.TabularInline):
#     model = Tramitacao
#     extra = 1

class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub', ]

# class EquipamentoPrevistoInline(admin.TabularInline):
#     model = EquipamentoPrevisto
#     extra = 2
#     raw_id_fields = ('equipamento',)

class AnexoAdmin(BaseModelAdmin):
    date_hierarchy = 'data_pub'
    exclude = ['data_pub', ]
    list_display = ('arquivo', 'descricao', 'data_pub', 'convenio')
    raw_id_fields = ('convenio',)
    search_fields = ('descricao', 'convenio__id', 'arquivo',
                     'convenio__casa_legislativa__nome')

class AcompanhaFilter(admin.filters.RelatedFieldListFilter):
    def __init__(self, *args, **kwargs):
        super(AcompanhaFilter, self).__init__(*args, **kwargs)
        servidores = Servidor.objects.filter(
            convenio__isnull=False).order_by('nome_completo').distinct()
        self.lookup_choices = [(x.id, x) for x in servidores]

class ConvenioAdmin(BaseModelAdmin):
    change_list_template = 'convenios/change_list.html'
    fieldsets = (
        (None,
            {'fields': ('casa_legislativa', 'num_processo_sf', 'num_convenio',
                        'projeto', 'data_sigi',)}
         ),
        (_(u"Acompanhamento no gabinete"),
         {'fields': ('data_solicitacao', 'data_sigad', 'tipo_solicitacao',
                     'status', 'acompanha', 'observacao',)}
        ),
        (_(u"Gestão do convênio"),
         {'fields': ('servico_gestao', 'servidor_gestao',)}
        ),
        (_(u'Datas'),
            {'fields': ('data_retorno_assinatura', 'duracao',
                        'data_pub_diario',)}
         ),
    )
    readonly_fields = ('data_sigi',)
    actions = ['adicionar_convenios']
    inlines = (AnexosInline,)
    list_display = ('num_convenio', 'casa_legislativa', 'get_uf',
                    'status_convenio', 'link_sigad', 'data_retorno_assinatura',
                    'duracao', 'projeto', 'status', 'acompanha',)
    list_display_links = ('num_convenio', 'casa_legislativa',)
    list_filter = ('status', ('acompanha', AcompanhaFilter),
                   ('casa_legislativa__gerentes_interlegis',
                    GerentesInterlegisFilter), 'projeto',
                   'casa_legislativa__tipo', 'conveniada','equipada',
                   'casa_legislativa__municipio__uf',)
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

    def status_convenio(self, obj):
        if obj.pk is None:
            return ""
        status = obj.get_status()

        if status in [u"Vencido", u"Desistência", u"Cancelado"]:
            label = r"danger"
        elif status == u"Vigente":
            label = r"success"
        elif status == u"Pendente":
            label = r"warning"
        else:
            label = r"info"

        return u'<p class="label label-{label}">{status}</p>'.format(label=label, status=status)
    status_convenio.short_description = _(u"Status do convênio")
    status_convenio.allow_tags = True

    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return obj.get_sigad_url()

    link_sigad.short_description = _("Processo no Senado")
    link_sigad.allow_tags = True

    def changelist_view(self, request, extra_context=None):
        from sigi.apps.convenios.views import normaliza_data
        request.GET._mutable = True
        normaliza_data(request.GET, 'data_retorno_assinatura__gte')
        normaliza_data(request.GET, 'data_retorno_assinatura__lte')
        normaliza_data(request.GET, 'data_sigad__gte')
        normaliza_data(request.GET, 'data_sigad__lte')
        normaliza_data(request.GET, 'data_sigi__gte')
        normaliza_data(request.GET, 'data_sigi__lte')
        normaliza_data(request.GET, 'data_solicitacao__gte')
        normaliza_data(request.GET, 'data_solicitacao__lte')
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
admin.site.register(StatusConvenio)
admin.site.register(TipoSolicitacao)
admin.site.register(Convenio, ConvenioAdmin)
admin.site.register(EquipamentoPrevisto, EquipamentoPrevistoAdmin)
