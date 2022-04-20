from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from sigi.apps.convenios.models import (Projeto, StatusConvenio,
                                        TipoSolicitacao, Convenio,
                                        EquipamentoPrevisto, Anexo, Tramitacao,
                                        Gescon)
from sigi.apps.utils import queryset_ascii
from sigi.apps.servidores.models import Servidor
from sigi.apps.casas.admin import ConveniosInline, GerentesInterlegisFilter
from sigi.apps.utils.mixins import CartExportReportMixin, LabeledResourse
from django_weasyprint.views import WeasyTemplateResponse
from sigi.apps.utils.filters import DateRangeFilter

class ConvenioExportResourse(LabeledResourse):
    class Meta:
        model = Convenio
        fields = ('num_processo_sf', 'num_convenio', 'projeto__nome',
                  'casa_legislativa__nome', 'casa_legislativa__municipio__nome',
                  'casa_legislativa__municipio__uf__sigla', 'data_sigi',
                  'data_sigad', 'data_adesao', 'data_retorno_assinatura',
                  'data_solicitacao', 'atualizacao_gescon', 'observacao_gescon',
                  'tipo_solicitacao__nome', 'status__nome',
                  'acompanha__nome_completo', 'servidor_gestao__nome_completo',
                  'observacao')
        export_order = fields

class AnexosInline(admin.TabularInline):
    model = Anexo
    extra = 2
    exclude = ['data_pub', ]

class AnexoAdmin(admin.ModelAdmin):
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

@admin.register(Convenio)
class ConvenioAdmin(CartExportReportMixin, admin.ModelAdmin):
    fieldsets = (
        (None,
            {'fields': ('casa_legislativa', 'num_processo_sf', 'num_convenio',
                        'projeto', 'data_sigi',)}
         ),
        (_("Acompanhamento no gabinete"),
         {'fields': ('data_solicitacao', 'data_sigad', 'observacao',)}
        ),
        (_("Gestão do convênio"),
         {'fields': ('servico_gestao', 'servidor_gestao',)}
        ),
        (_('Datas'),
         {'fields': ('data_retorno_assinatura', 'data_termino_vigencia',
                     'data_pub_diario',)}
         ),
        (_('Gescon'),
         {'fields': ('atualizacao_gescon', 'observacao_gescon', 'link_gescon')}
        ),
    )
    readonly_fields = ('data_sigi', 'atualizacao_gescon', 'observacao_gescon',
                       'link_gescon')
    inlines = (AnexosInline,)
    list_display = ('num_convenio', 'projeto','casa_legislativa', 'get_uf',
                    'status_convenio', 'link_sigad', 'data_retorno_assinatura',
                    'data_termino_vigencia',)
    list_display_links = ('num_convenio', 'casa_legislativa',)
    list_filter = (
        ('data_retorno_assinatura', DateRangeFilter),
        ('data_sigi', DateRangeFilter), ('data_solicitacao', DateRangeFilter),
        ('data_sigad', DateRangeFilter),
        ('casa_legislativa__gerentes_interlegis', GerentesInterlegisFilter),
        'projeto', 'casa_legislativa__tipo', 'conveniada','equipada',
        'casa_legislativa__municipio__uf',
    )
    ordering = ('casa_legislativa', '-data_retorno_assinatura')
    raw_id_fields = ('casa_legislativa',)
    get_queryset = queryset_ascii
    search_fields = ('id', 'casa_legislativa__search_text',
                     'casa_legislativa__sigla', 'num_processo_sf',
                     'num_convenio')
    resource_class = ConvenioExportResourse
    reports = [
        'report_convenios',
        'report_convenios_camaras',
        'report_convenios_assembleia',
    ]

    def get_queryset(self, request):
        queryset = super(ConvenioAdmin, self).get_queryset(request)
        return queryset

    def get_uf(self, obj):
        return obj.casa_legislativa.municipio.uf.sigla
    get_uf.short_description = _('UF')
    get_uf.admin_order_field = 'casa_legislativa__municipio__uf__sigla'

    def status_convenio(self, obj):
        if obj.pk is None:
            return ""
        status = obj.get_status()

        if status in ["Vencido", "Desistência", "Cancelado"]:
            label = r"danger"
        elif status == "Vigente":
            label = r"success"
        elif status == "Pendente":
            label = r"warning"
        else:
            label = r"info"
        return mark_safe(f'<p class="label label-{label}">{status}</p>')
    status_convenio.short_description = _("Status do convênio")

    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return mark_safe(obj.get_sigad_url())
    link_sigad.short_description = _("Processo no Senado")

    def link_gescon(self, obj):
        if not obj.id_contrato_gescon:
            return ""
        return mark_safe(
            f"<a href='https://adm.senado.gov.br/gestao-contratos/api/"
            f"contratos/buscaTexto/{obj.id_contrato_gescon}'>"
            f"https://adm.senado.gov.br/gestao-contratos/api/"
            f"{obj.id_contrato_gescon}</a>")
    link_gescon.short_description = _("Download MINUTA ASSINADA do Gescon")

    def report_convenios(self, request):
        context = {
            'convenios': self.get_queryset(request),
            'title': _('Relatório de convenios'),
        }
        return WeasyTemplateResponse(
            filename='relatorio_convenios.pdf',
            request=request,
            template="convenios/convenios_report.html",
            context=context,
            content_type='application/pdf',
        )
    report_convenios.title = _('Relatório de convênios')


    def report_convenios_camaras(self, request):
        context = {
            'convenios': self.get_queryset(request).filter(casa_legislativa__tipo__legislativo = False),
            'title': _('Relatório de convenios de camaras municipais'),
        }
        return WeasyTemplateResponse(
            filename='relatorio_convenios.pdf',
            request=request,
            template="convenios/convenios_report.html",
            context=context,
            content_type='application/pdf',
        )
    report_convenios_camaras.title = _('Relatório de convênios de camaras municipais')


    def report_convenios_assembleia(self, request):
        context = {
            'convenios': self.get_queryset(request).filter(casa_legislativa__tipo__legislativo = True),
            'title': _('Relatório de convenios de assembleias legislativas'),
        }
        return WeasyTemplateResponse(
            filename='relatorio_convenios.pdf',
            request=request,
            template="convenios/convenios_report.html",
            context=context,
            content_type='application/pdf',
        )
    report_convenios_assembleia.title = _('Relatório de convênios de assembleias legislativas')


    # def relatorio(self, request, queryset):
    #     # queryset.order_by('casa_legislativa__municipio__uf')
    #     response = HttpResponse(content_type='application/pdf')
    #     report = ConvenioReport(queryset=queryset)
    #     report.generate_by(PDFGenerator, filename=response)
    #     return response
    # relatorio.short_description = _('Exportar convênios selecionados para PDF')

    # def adicionar_convenios(self, request, queryset):
    #     if 'carrinho_convenios' in request.session:
    #         q1 = len(request.session['carrinho_convenios'])
    #     else:
    #         q1 = 0
    #     adicionar_convenios_carrinho(request, queryset=queryset)
    #     q2 = len(request.session['carrinho_convenios'])
    #     quant = q2 - q1
    #     if quant:
    #         self.message_user(request, str(q2 - q1) + _(" Convênios adicionados no carrinho"))
    #     else:
    #         self.message_user(request, _("Os Convênios selecionados já foram adicionadas anteriormente"))
    #     return HttpResponseRedirect('.')
    # adicionar_convenios.short_description = _("Armazenar convênios no carrinho para exportar")

    def get_actions(self, request):
        actions = super(ConvenioAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

@admin.register(EquipamentoPrevisto)
class EquipamentoPrevistoAdmin(admin.ModelAdmin):
    list_display = ('convenio', 'equipamento', 'quantidade')
    list_display_links = ('convenio', 'equipamento')
    ordering = ('convenio', 'equipamento')
    raw_id_fields = ('convenio', 'equipamento')
    search_fields = ('convenio__id', 'equipamento__fabricante__nome',
                     'equipamento__modelo__modelo', 'equipamento__modelo__tipo__tipo')

@admin.register(Gescon)
class GesconAdmin(admin.ModelAdmin):
    list_display = ('url_gescon', 'email',)
    exclude = ['ultima_importacao',]

admin.site.register(Projeto)
admin.site.register(StatusConvenio)
admin.site.register(TipoSolicitacao)
