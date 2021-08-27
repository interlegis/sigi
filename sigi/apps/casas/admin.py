# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from image_cropping import ImageCroppingMixin

from sigi.apps.casas.forms import OrgaoForm
from sigi.apps.casas.models import Orgao, Presidente, Funcionario, TipoOrgao
from sigi.apps.casas.views import report_complete, labels_report, export_csv, \
    labels_report_sem_presidente, report, \
    adicionar_casas_carrinho
from sigi.apps.contatos.models import Telefone
from sigi.apps.convenios.models import Convenio, Projeto
# from sigi.apps.diagnosticos.models import Diagnostico
# from sigi.apps.inventario.models import Bem
from sigi.apps.metas.models import PlanoDiretor
from sigi.apps.ocorrencias.models import Ocorrencia
# from sigi.apps.parlamentares.models import Legislatura
from sigi.apps.servicos.models import Servico, TipoServico
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils import queryset_ascii
from sigi.apps.utils.base_admin import BaseModelAdmin


class TelefonesInline(generic.GenericTabularInline):
    model = Telefone
    readonly_fields = ('ult_alteracao',)
    extra = 1


class PresidenteInline(admin.StackedInline):
    model = Presidente
    fields = ('nome', 'sexo', 'data_nascimento', 'nota', 'email',
              'tempo_de_servico', 'ult_alteracao', 'endereco', 'municipio',
              'bairro', 'cep', 'redes_sociais',)
    raw_id_fields = ('municipio',)
    # fieldsets = ((None, {
    #     'fields': (
    #         ('nome', 'sexo', 'data_nascimento'),
    #         ('nota', 'email', 'tempo_de_servico'),
    #         ('ult_alteracao',),
    #     )
    # }),)
#     exclude = ['setor', 'cargo', 'funcao']
    readonly_fields = ('ult_alteracao',)
    extra = 1
    max_num = 1
    verbose_name_plural = _(u'Presidente')


class FuncionariosInline(admin.StackedInline):
    model = Funcionario
    fields = ('nome', 'sexo', 'data_nascimento', 'nota', 'email', 'cargo',
              'funcao', 'setor', 'tempo_de_servico', 'ult_alteracao',
              'endereco', 'municipio', 'bairro', 'cep', 'redes_sociais',
              'desativado', 'observacoes')
    raw_id_fields = ('municipio',)
    # fieldsets = ((None, {
    #     'fields': (
    #         ('nome', 'sexo', 'data_nascimento'),
    #         ('nota', 'email'),
    #         ('cargo', 'funcao', 'setor'),
    #         ('tempo_de_servico', 'ult_alteracao'),
    #         ('endereco', 'municipio'),
    #         ('bairro', 'cep'),
    #         ('redes_sociais'),
    #         ('desativado', 'observacoes'),
    #     )
    # }),)
    readonly_fields = ('ult_alteracao',)
    extra = 1
    inlines = (TelefonesInline,)

    def get_queryset(self, request):
        return (self.model.objects.exclude(cargo='Presidente')
        .exclude(desativado=True).extra(select={'ult_null': 'ult_alteracao is null'})
        .order_by('ult_null', '-ult_alteracao')
            # A função extra foi usada para quando existir um registro com o campo igual a null não aparecer na frente dos mais novos
        )


class ConveniosInline(admin.TabularInline):
    model = Convenio
    fieldsets = (
        (None, {'fields': (
            ('link_sigad', 'status_convenio', 'num_convenio',
             'projeto', 'observacao'),
            ('data_retorno_assinatura', 'data_pub_diario',),
            ('get_anexos',),
            ('link_convenio',),
        )}),
    )
    readonly_fields = ['link_convenio', 'link_sigad', 'status_convenio',
                       'num_convenio', 'projeto', 'observacao', 'data_adesao',
                       'data_retorno_assinatura', 'data_termo_aceite',
                       'data_pub_diario', 'data_devolucao_via',
                       'data_postagem_correio', 'data_devolucao_sem_assinatura',
                       'data_retorno_sem_assinatura', 'get_anexos']
    extra = 0
    can_delete = False
    template = 'admin/casas/convenios_inline.html'
    ordering = ('-data_retorno_assinatura',)

    def has_add_permission(self, request):
        return False

#     def get_tramitacoes(self, obj):
#         return '<br/>'.join([t.__unicode__() for t in obj.tramitacao_set.all()])
#
#     get_tramitacoes.short_description = _(u'Tramitações')
#     get_tramitacoes.allow_tags = True
#
    def get_anexos(self, obj):
        return '<br/>'.join(['<a href="%s" target="_blank">%s</a>' % (a.arquivo.url, a.__unicode__()) for a in obj.anexo_set.all()])
    get_anexos.short_description = _(u'Anexos')
    get_anexos.allow_tags = True
#
#     def get_equipamentos(self, obj):
#         return '<br/>'.join([e.__unicode__() for e in obj.equipamentoprevisto_set.all()])
#
#     get_equipamentos.short_description = _(u'Equipamentos previstos')
#     get_equipamentos.allow_tags = True

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


    def link_convenio(self, obj):
        if obj.pk is None:
            return ""
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.module_name), args=[obj.pk])
        url = url + '?_popup=1'
        return """<input id="edit_convenio-%s" type="hidden"/>
          <a id="lookup_edit_convenio-%s" href="%s" class="changelink" onclick="return showRelatedObjectLookupPopup(this)">
            Editar
          </a>""" % (obj.pk, obj.pk, url)

    link_convenio.short_description = _(u'Editar convenio')
    link_convenio.allow_tags = True

    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return obj.get_sigad_url()

    link_sigad.short_description = _("Processo no Senado")
    link_sigad.allow_tags = True

# class LegislaturaInline(admin.TabularInline):
#     model = Legislatura
#     fields = ['numero', 'data_inicio', 'data_fim', 'data_eleicao', 'total_parlamentares', 'link_parlamentares', ]
#     readonly_fields = ['link_parlamentares', ]

#     def link_parlamentares(self, obj):
#         if obj.pk is None:
#             return ""
#         from django.core.urlresolvers import reverse
#         url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.module_name), args=[obj.pk])
#         url = url + '?_popup=1'
#         return """<input id="edit_legislatura-%s" type="hidden"/>
#           <a id="lookup_edit_legislatura-%s" href="%s" class="changelink" onclick="return showRelatedObjectLookupPopup(this)">
#             Editar
#           </a>""" % (obj.pk, obj.pk, url)

#     link_parlamentares.short_description = _(u'Parlamentares')
#     link_parlamentares.allow_tags = True

# class DiagnosticoInline(admin.TabularInline):
#     model = Diagnostico
#     fields = ['data_visita_inicio', 'data_visita_fim', 'publicado', 'data_publicacao', 'responsavel', 'link_diagnostico', ]
#     readonly_fields = ['data_visita_inicio', 'data_visita_fim', 'publicado', 'data_publicacao', 'responsavel', 'link_diagnostico', ]
#     extra = 0
#     max_num = 0
#     can_delete = False

#     def link_diagnostico(self, obj):
#         if obj.pk is None:
#             return ""
#         url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.module_name), args=["%s.pdf" % obj.pk])
#         return """<input id="edit_diagnostico-%s" type="hidden"/>
#           <a id="lookup_edit_diagnostico-%s" href="%s" class="button" target="_blank">
#             Abrir PDF
#           </a>""" % (obj.pk, obj.pk, url)

#     link_diagnostico.short_description = _(u'Ver PDF')
#     link_diagnostico.allow_tags = True

# class BemInline(admin.TabularInline):
#     model = Bem

class ServicoInline(admin.TabularInline):
    model = Servico
    fields = ('link_url', 'contato_tecnico', 'contato_administrativo',
              'hospedagem_interlegis', 'data_ativacao', 'data_alteracao',
              'data_desativacao')
    readonly_fields = ['link_url', 'contato_tecnico', 'contato_administrativo',
                       'hospedagem_interlegis', 'data_ativacao',
                       'data_alteracao', 'data_desativacao']
    extra = 0
    max_num = 0
    can_delete = False

    def link_url(self, servico):
        if servico.data_desativacao is not None:
            return servico.url
        return u'<a href="{url}" target="_blank">{url}</a>'.format(url=servico.url)
    link_url.short_description = _(u'URL do serviço')
    link_url.allow_tags = True

    ordering = ('-data_alteracao',)

# class PlanoDiretorInline(admin.TabularInline):
#     model = PlanoDiretor

class OcorrenciaInline(admin.TabularInline):
    model = Ocorrencia
    fields = ('data_criacao', 'assunto', 'prioridade', 'status', 'data_modificacao', 'setor_responsavel', 'link_editar',)
    readonly_fields = ('data_criacao', 'assunto', 'prioridade', 'status', 'data_modificacao', 'setor_responsavel', 'link_editar',)
    extra = 0
    max_num = 0
    can_delete = False
    template = 'admin/casas/ocorrencia_inline.html'

    ordering = ('-data_modificacao',)

    def link_editar(self, obj):
        if obj.pk is None:
            return ""
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.module_name), args=[obj.pk])
        return u"""<input id="edit_ocorrencia-%s" type="hidden"/>
        <a id="lookup_edit_ocorrencia-%s" href="%s" class="button" target="_blank"
          onclick="return showRelatedObjectLookupPopup(this);">%s</a>""" % (obj.pk, obj.pk, url, _(u'Editar'))

    link_editar.short_description = _(u'Editar')
    link_editar.allow_tags = True


class GerentesInterlegisFilter(admin.filters.RelatedFieldListFilter):

    def __init__(self, *args, **kwargs):
        super(GerentesInterlegisFilter, self).__init__(*args, **kwargs)
        gerentes = Servidor.objects.filter(casas_que_gerencia__isnull=False).order_by('nome_completo').distinct()
        self.lookup_choices = [(x.id, x) for x in gerentes]


class ConvenioFilter(admin.SimpleListFilter):
    title = _(u"Tipo de convênio")
    parameter_name = 'convenio'

    def lookups(self, request, model_admin):
        return (
            ('SC', _(u"Sem nenhum convênio")),
            ('CC', _(u"Com algum convênio"))
        ) + tuple([(p.pk, p.sigla) for p in Projeto.objects.all()])

    def queryset(self, request, queryset):
        if self.value() is not None:
            if self.value() == 'SC':
                queryset = queryset.filter(convenio=None)
            elif self.value() == 'CC':
                queryset = queryset.exclude(convenio=None)
            else:
                queryset = queryset.filter(convenio__projeto_id=self.value())

        return queryset.distinct('municipio__uf__nome', 'nome')


class ServicoFilter(admin.SimpleListFilter):
    title = _(u"Serviço")
    parameter_name = 'servico'

    def lookups(self, request, model_admin):
        return (
            ('SS', _(u"Sem nenhum serviço")),
            ('CS', _(u"Com algum serviço")),
            ('CH', _(u"Com algum serviço de hospedagem")),
            ('CR', _(u"Apenas serviço de registro")),
        ) + tuple([(p.pk, p.nome) for p in TipoServico.objects.all()])

    def queryset(self, request, queryset):
        if self.value() is not None:
            if self.value() == 'SS':
                queryset = queryset.filter(servico=None)
            elif self.value() == 'CS':
                queryset = queryset.exclude(servico=None).filter(
                    servico__data_desativacao__isnull=True)
            elif self.value() == 'CR':
                queryset = queryset.exclude(servico__tipo_servico__modo='H') \
                                    .exclude(servico=None)
            elif self.value() == 'CH':
                queryset = queryset.filter(
                    servico__tipo_servico__modo='H',
                    servico__data_desativacao__isnull=True
                )
            else:
                queryset = queryset.filter(
                    servico__tipo_servico_id=self.value()
                )

        return queryset.distinct('municipio__uf__nome', 'nome')

@admin.register(Orgao)
class OrgaoAdmin(ImageCroppingMixin, BaseModelAdmin):
    form = OrgaoForm
    actions = ['adicionar_casas', ]
    inlines = (TelefonesInline, PresidenteInline, FuncionariosInline,
               ConveniosInline, ServicoInline, OcorrenciaInline,)
    list_display = ('id', 'sigla', 'nome', 'get_uf', 'get_gerentes', 'get_convenios',
                    'get_servicos')
    list_display_links = ('sigla', 'nome',)
    list_filter = ('tipo', ('gerentes_interlegis', GerentesInterlegisFilter),
                   'municipio__uf__nome', ConvenioFilter, ServicoFilter,
                   'inclusao_digital',)
    ordering = ('municipio__uf__nome', 'nome')
    queryset = queryset_ascii
    fieldsets = (
        (None, {
            'fields': ('tipo', 'nome', 'sigla', 'cnpj', 'num_parlamentares',
                       'gerentes_interlegis')
        }),
        (_(u'Endereço'), {
            'fields': ('data_instalacao', 'logradouro', 'bairro',
                       'municipio', 'cep', 'ult_alt_endereco'),
        }),
        (_(u'Presença na Internet'), {
            'fields': ('inclusao_digital', 'data_levantamento', 'pesquisador',
                       'pagina_web', 'email', 'obs_pesquisa',)
        }),
        (_(u'Outras informações'), {
            'fields': ('observacoes', 'horario_funcionamento', 'foto',
                       'recorte'),
        }),
    )
    raw_id_fields = ('municipio',)
    readonly_fields = ['num_parlamentares', 'gerentes_interlegis',]
    search_fields = ('search_text', 'sigla', 'cnpj', 'bairro', 'logradouro',
                     'cep', 'municipio__nome', 'municipio__uf__nome',
                     'municipio__codigo_ibge', 'pagina_web', 'observacoes')

    def get_uf(self, obj):
        return obj.municipio.uf.nome
    get_uf.short_description = _(u'Unidade da Federação')
    get_uf.admin_order_field = 'municipio__uf__nome'

    def get_gerentes(self, obj):
        return obj.lista_gerentes()
    get_gerentes.short_description = _(u'Gerente Interlegis')
    get_gerentes.allow_tags = True

    def get_convenios(self, obj):
        return '<ul>' + ''.join(['<li>%s</li>' % c.__unicode__()
                                 for c in obj.convenio_set.all()]) + '</ul>'
    get_convenios.short_description = _(u'Convênios')
    get_convenios.allow_tags = True

    def get_servicos(self, obj):
        return u'<ul>' + u''.join(
            [u'<li><a href="{url}" target="_blank">{servico}</a></li>'.format(
                url=s.url, servico=s.__unicode__()) for s in
             obj.servico_set.filter(data_desativacao__isnull=True)]) + u'</ul>'
    get_servicos.short_description = _(u'Serviços')
    get_servicos.allow_tags = True

    def changelist_view(self, request, extra_context=None):
        return super(OrgaoAdmin, self).changelist_view(
            request,
            extra_context={'query_str': '?' + request.META['QUERY_STRING']}
        )

    def lookup_allowed(self, lookup, value):
        return (super(OrgaoAdmin, self).lookup_allowed(lookup, value) or
                lookup in ['tipo__legislativo__exact',
                           'tipo__sigla__exact',
                           'municipio__uf__codigo_ibge__exact',
                           'convenio__projeto__id__exact'])

    def etiqueta(self, request, queryset):
        return labels_report(request, queryset=queryset)
    etiqueta.short_description = _(u"Gerar etiqueta(s) da(s) casa(s) "
                                   u"selecionada(s)")

    def etiqueta_sem_presidente(self, request, queryset):
        return labels_report_sem_presidente(request, queryset=queryset)
    etiqueta_sem_presidente.short_description = _(u"Gerar etiqueta(s) sem "
                                                  u"presidente da(s) casa(s) "
                                                  u"selecionada(s)")

    def relatorio(self, request, queryset):
        return report(request, queryset=queryset)
    relatorio.short_description = _(u"Exportar a(s) casa(s) selecionada(s) "
                                    u"para PDF")

    def relatorio_completo(self, request, queryset):
        return report_complete(request, queryset=queryset)
    relatorio_completo.short_description = _(u"Gerar relatório completo da(s) "
                                             u"casa(s) selecionada(s)")

    def relatorio_csv(self, request, queryset):
        return export_csv(request)
    relatorio_csv.short_description = _(u"Exportar casa(s) selecionada(s) "
                                        u"para CSV")

    def adicionar_casas(self, request, queryset):
        if 'carrinho_casas' in request.session:
            # if request.session.has_key('carrinho_casas'):
            q1 = len(request.session['carrinho_casas'])
        else:
            q1 = 0
        response = adicionar_casas_carrinho(request, queryset=queryset)
        q2 = len(request.session['carrinho_casas'])
        quant = q2 - q1
        if quant:
            self.message_user(request, str(q2 - q1) + " " +
                              _(u"Casas Legislativas adicionadas no carrinho"))
        else:
            self.message_user(request, _(u"As Casas Legislativas selecionadas "
                                         u"já foram adicionadas anteriormente"))
        return HttpResponseRedirect('.')

    adicionar_casas.short_description = _(u"Armazenar casas no carrinho para "
                                          u"exportar")

    def get_actions(self, request):
        actions = super(OrgaoAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(TipoOrgao)
