# -*- coding: utf-8 -*-

from unicodedata import name
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
#from geraldo.site.newsite.django_1_0.django.forms import extras
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
    verbose_name_plural = _('Presidente')
    def get_queryset(self, request):
        return (self.model.objects.exclude(desativado=True)
        .extra(select={'ult_null': 'ult_alteracao is null'})
        .order_by('ult_null', '-ult_alteracao')
            # A função extra foi usada para quando existir um registro com o campo igual a null não aparecer na frente dos mais novos
        )

class ContatoInterlegisInline(admin.StackedInline):
    model = Funcionario
    fields = ('nome', 'sexo', 'data_nascimento', 'nota', 'email', 'cargo',
              'funcao', 'setor', 'tempo_de_servico', 'ult_alteracao',
              'endereco', 'municipio', 'bairro', 'cep', 'redes_sociais',
              'desativado', 'observacoes')
    raw_id_fields = ('municipio',)
    readonly_fields = ('ult_alteracao',)
    extra = 1
    inlines = (TelefonesInline,)
    verbose_name_plural = _('Contato(s) Interlegis Vigente(s)')
    def get_queryset(self, request):
        return (self.model.objects.filter(setor='contato_interlegis')
        .extra(select={'ult_null': 'ult_alteracao is null'}).order_by('-ult_alteracao')
        )
    def get_extra(self, request, obj=None , **kwargs):
        extra = 0
        return extra

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
    verbose_name_plural = _('Outros Contatos da Casa')

    def get_queryset(self, request):
        return (self.model.objects.exclude(cargo='Presidente',)
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
#     get_tramitacoes.short_description = _('Tramitações')
#     get_tramitacoes.allow_tags = True
#
    def get_anexos(self, obj):
        return '<br/>'.join(['<a href="%s" target="_blank">%s</a>' % (a.arquivo.url, a.__unicode__()) for a in obj.anexo_set.all()])
    get_anexos.short_description = _('Anexos')
    get_anexos.allow_tags = True
#
#     def get_equipamentos(self, obj):
#         return '<br/>'.join([e.__unicode__() for e in obj.equipamentoprevisto_set.all()])
#
#     get_equipamentos.short_description = _('Equipamentos previstos')
#     get_equipamentos.allow_tags = True

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

        return '<p class="label label-{label}">{status}</p>'.format(label=label, status=status)
    status_convenio.short_description = _("Status do convênio")
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

    link_convenio.short_description = _('Editar convenio')
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

#     link_parlamentares.short_description = _('Parlamentares')
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

#     link_diagnostico.short_description = _('Ver PDF')
#     link_diagnostico.allow_tags = True

# class BemInline(admin.TabularInline):
#     model = Bem

class ServicoInline(admin.TabularInline):
    model = Servico
    fields = ('link_url', 'contato_tecnico', 'contato_administrativo',
              'hospedagem_interlegis', 'data_ativacao', 'data_alteracao',
              'data_desativacao', 'link_servico')
    readonly_fields = ['link_url', 'contato_tecnico', 'contato_administrativo',
                       'hospedagem_interlegis', 'data_ativacao',
                       'data_alteracao', 'data_desativacao', 'link_servico']
    extra = 0
    max_num = 0
    can_delete = False

    def link_url(self, servico):
        if servico.data_desativacao is not None:
            return servico.url
        return '<a href="{url}" target="_blank">{url}</a>'.format(url=servico.url)
    link_url.short_description = _('URL do serviço')
    link_url.allow_tags = True

    ordering = ('-data_alteracao',)

    def link_servico(self, obj):
        if obj.pk is None:
            return ""
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.module_name), args=[obj.pk])
        url = url + '?_popup=1'
        return """<input id="edit_convenio-%s" type="hidden"/>
          <a id="lookup_edit_convenio-%s" href="%s" class="changelink" onclick="return showRelatedObjectLookupPopup(this)">
            Editar
          </a>""" % (obj.pk, obj.pk, url)

    link_servico.short_description = _('Editar Serviço')
    link_servico.allow_tags = True

    def has_add_permission(self, request):
        return False

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
        return """<input id="edit_ocorrencia-%s" type="hidden"/>
        <a id="lookup_edit_ocorrencia-%s" href="%s" class="button" target="_blank"
          onclick="return showRelatedObjectLookupPopup(this);">%s</a>""" % (obj.pk, obj.pk, url, _('Editar'))

    link_editar.short_description = _('Editar')
    link_editar.allow_tags = True


class GerentesInterlegisFilter(admin.filters.RelatedFieldListFilter):

    def __init__(self, *args, **kwargs):
        super(GerentesInterlegisFilter, self).__init__(*args, **kwargs)
        gerentes = Servidor.objects.filter(casas_que_gerencia__isnull=False).order_by('nome_completo').distinct()
        self.lookup_choices = [(x.id, x) for x in gerentes]


class ConvenioFilter(admin.SimpleListFilter):
    title = _("Tipo de convênio")
    parameter_name = 'convenio'

    def lookups(self, request, model_admin):
        return (
            ('SC', _("Sem nenhum convênio")),
            ('CC', _("Com algum convênio")),
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

class ExcluirConvenioFilter(admin.SimpleListFilter):
    title=_("Excluir convênio da pesquisa")
    parameter_name = 'excluir_convenio'

    def lookups(self, request, model_admin):
        return tuple([(p.pk, p.sigla) for p in Projeto.objects.all()])

    def queryset(self, request, queryset):
        if (self.value() is None):
            return queryset
        else:
            queryset = queryset.exclude(convenio__projeto_id=self.value()).distinct('municipio__uf__nome', 'nome')
        return queryset

class ServicoFilter(admin.SimpleListFilter):
    title = _("Serviço")
    parameter_name = 'servico'

    def lookups(self, request, model_admin):
        return (
            ('SS', _("Sem nenhum serviço")),
            ('CS', _("Com algum serviço")),
            ('CH', _("Com algum serviço de hospedagem")),
            ('CR', _("Apenas serviço de registro")),
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

class ServicoAtivoFilter(admin.SimpleListFilter):
    title = _("Serviço ativo")
    parameter_name = 'ativo'

    def lookups(self, request, model_admin):
        return (
            ('ativo', _("Ativo")),
            ('desativado', _("Desativado")),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            if self.value() == 'ativo':
                queryset = queryset.filter(servico__data_desativacao__isnull=True)
            else:
                queryset = queryset.filter(servico__data_desativacao__isnull=False)
        return queryset
@admin.register(Orgao)
class OrgaoAdmin(ImageCroppingMixin, BaseModelAdmin):
    form = OrgaoForm
    actions = ['adicionar_casas', ]
    inlines = (TelefonesInline, PresidenteInline, ContatoInterlegisInline, FuncionariosInline,
               ConveniosInline, ServicoInline, OcorrenciaInline,)
    list_display = ('id', 'sigla', 'nome', 'get_uf', 'get_gerentes', 'get_convenios',
                    'get_servicos')
    list_display_links = ('sigla', 'nome',)
    list_filter = ('tipo', ('gerentes_interlegis', GerentesInterlegisFilter),
                   'municipio__uf__nome', ConvenioFilter, ServicoAtivoFilter, ExcluirConvenioFilter, ServicoFilter,
                   'inclusao_digital',)
    ordering = ('municipio__uf__nome', 'nome')
    queryset = queryset_ascii
    fieldsets = (
        (None, {
            'fields': ('tipo', 'nome', 'sigla', 'cnpj', 'num_parlamentares',
                       'gerentes_interlegis')
        }),
        (_('Endereço'), {
            'fields': ('data_instalacao', 'logradouro', 'bairro',
                       'municipio', 'cep', 'ult_alt_endereco'),
        }),
        (_('Presença na Internet'), {
            'fields': ('inclusao_digital', 'data_levantamento', 'pesquisador',
                       'pagina_web', 'email', 'obs_pesquisa',)
        }),
        (_('Outras informações'), {
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
    get_uf.short_description = _('Unidade da Federação')
    get_uf.admin_order_field = 'municipio__uf__nome'

    def get_gerentes(self, obj):
        return obj.lista_gerentes()
    get_gerentes.short_description = _('Gerente Interlegis')
    get_gerentes.allow_tags = True

    def get_convenios(self, obj):
        return '<ul>' + ''.join(['<li>%s</li>' % c.__unicode__()
                                 for c in obj.convenio_set.all()]) + '</ul>'
    get_convenios.short_description = _('Convênios')
    get_convenios.allow_tags = True

    def get_servicos(self, obj):
        return '<ul>' + ''.join(
            ['<li><a href="{url}" target="_blank">{servico}</a></li>'.format(
                url=s.url, servico=s.__unicode__()) for s in
             obj.servico_set.filter(data_desativacao__isnull=True)]) + '</ul>'
    get_servicos.short_description = _('Serviços')
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
    etiqueta.short_description = _("Gerar etiqueta(s) da(s) casa(s) "
                                   "selecionada(s)")

    def etiqueta_sem_presidente(self, request, queryset):
        return labels_report_sem_presidente(request, queryset=queryset)
    etiqueta_sem_presidente.short_description = _("Gerar etiqueta(s) sem "
                                                  "presidente da(s) casa(s) "
                                                  "selecionada(s)")

    def relatorio(self, request, queryset):
        return report(request, queryset=queryset)
    relatorio.short_description = _("Exportar a(s) casa(s) selecionada(s) "
                                    "para PDF")

    def relatorio_completo(self, request, queryset):
        return report_complete(request, queryset=queryset)
    relatorio_completo.short_description = _("Gerar relatório completo da(s) "
                                             "casa(s) selecionada(s)")

    def relatorio_csv(self, request, queryset):
        return export_csv(request)
    relatorio_csv.short_description = _("Exportar casa(s) selecionada(s) "
                                        "para CSV")

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
                              _("Casas Legislativas adicionadas no carrinho"))
        else:
            self.message_user(request, _("As Casas Legislativas selecionadas "
                                         "já foram adicionadas anteriormente"))
        return HttpResponseRedirect('.')

    adicionar_casas.short_description = _("Armazenar casas no carrinho para "
                                          "exportar")

    def get_actions(self, request):
        actions = super(OrgaoAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(TipoOrgao)
