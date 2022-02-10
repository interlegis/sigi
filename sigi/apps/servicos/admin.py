from datetime import date, timedelta
import resource
from django.contrib import admin
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.forms.models import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import gettext as _
from import_export.fields import Field
from sigi.apps.casas.admin import FuncionariosInline, GerentesInterlegisFilter
from sigi.apps.casas.models import Orgao
from sigi.apps.servicos.models import (Servico, LogServico, CasaAtendida,
                                       TipoServico)
from sigi.apps.utils.mixins import CartExportMixin, LabeledResourse

class ServicoExportResourse(LabeledResourse):
    telefone_casa = Field(column_name='Casa Legislativa/telefone')
    hospedagem_interlegis = Field(column_name='hospedagem no interlegis')
    class Meta:
        model = Servico
        fields = ('casa_legislativa__nome', 'casa_legislativa__municipio__nome',
                  'casa_legislativa__municipio__uf__sigla',
                  'casa_legislativa__email', 'telefone_casa',
                  'contato_tecnico__nome', 'contato_tecnico__email',
                  'contato_tecnico__nota', 'tipo_servico__nome', 'url',
                  'hospedagem_interlegis', 'data_ativacao', 'data_desativacao',
                  'motivo_desativacao', 'data_ultimo_uso', 'erro_atualizacao')
        export_order = fields
    def dehydrate_telefone_casa(self, servico):
        return servico.casa_legislativa.telefone
    def dehydrate_hospedagem_interlegis(self, servico):
        if servico.hospedagem_interlegis:
            return _("Sim")
        else:
            return _("Não")


class LogServicoInline(admin.StackedInline):
    model = LogServico
    Fieldset = ((None, {'fields': (('data', 'descricao'), 'log')}))
    extra = 1

class ServicoFormAdmin(ModelForm):
    class Meta:
        model = Servico
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ServicoFormAdmin, self).__init__(*args, **kwargs)

        self.fields['contato_tecnico'].choices = ()
        self.fields['contato_administrativo'].choices = ()

        if self.instance.casa_legislativa_id:
            id_casa = self.instance.casa_legislativa_id
        elif 'initial' in kwargs and 'id_casa' in kwargs['initial']:
            id_casa = kwargs['initial']['id_casa']
            self.instance.casa_legislativa_id = id_casa
        else:
            id_casa = None

        if id_casa:
            casa = CasaAtendida.objects.get(pk=id_casa)
            contatos = [
                (f.id, force_str(f)) for f in casa.funcionario_set.all()
            ]
            self.fields['contato_tecnico'].choices = contatos
            self.fields['contato_administrativo'].choices = contatos

@admin.register(TipoServico)
class TipoServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sigla', 'nome', 'qtde_casas_atendidas', )
    ordering = ['id']

class DataUtimoUsoFilter(admin.SimpleListFilter):
    title = _("Atualização")
    parameter_name = 'atualizacao'

    def lookups(self, request, model_admin):
        return (
            ('err', _("Erro na verificação")),
            ('year', _("Sem atualização há um ano ou mais")),
            ('semester', _("Sem atualização de seis meses a um ano")),
            ('quarter', _("Sem atualização de três a seis meses")),
            ('month', _("Sem atualização de um a três meses")),
            ('week', _("Sem atualização de uma semana a um mês")),
            ('updated', _("Atualizado na última semana")),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            queryset = queryset.exclude(tipo_servico__string_pesquisa="")
            if self.value() == 'err':
                queryset = queryset.exclude(erro_atualizacao="")
            elif self.value() == 'year':
                limite = date.today() - timedelta(days=365)
                queryset = queryset.filter(data_ultimo_uso__lte=limite)
            else:
                de = date.today() - (
                    timedelta(days=365) if self.value() == 'semester' else
                    timedelta(days=6*30) if self.value() == 'quarter' else
                    timedelta(days=3*30) if self.value() == 'month' else
                    timedelta(days=30) if self.value() == 'week' else
                    timedelta(days=0)
                )
                ate = date.today() - (
                    timedelta(days=6*30) if self.value() == 'semester' else
                    timedelta(days=3*30) if self.value() == 'quarter' else
                    timedelta(days=30) if self.value() == 'month' else
                    timedelta(days=7) if self.value() == 'week' else
                    timedelta(days=0)
                )
                queryset = queryset.filter(data_ultimo_uso__range=(de, ate))
        return queryset

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
                queryset = queryset.filter(data_desativacao__isnull=True)
            else:
                queryset = queryset.filter(data_desativacao__isnull=False)
        return queryset

@admin.register(Servico)
class ServicoAdmin(CartExportMixin, admin.ModelAdmin):
    form = ServicoFormAdmin
    actions = ['calcular_data_uso', ]
    list_display = ('casa_legislativa', 'get_codigo_interlegis', 'get_uf',
                    'tipo_servico', 'hospedagem_interlegis', 'data_ativacao',
                    'data_desativacao', 'getUrl', 'data_ultimo_uso',
                    'get_link_erro')
    fieldsets = ((None, {
        'fields': ('casa_legislativa', 'data_ativacao',)
    }),
        (_('Serviço'), {
            'fields': ('tipo_servico', ('url', 'hospedagem_interlegis'),
                       ('nome_servidor', 'porta_servico', 'senha_inicial'),)
        }),
        (_('Contatos'), {
            'fields': ('contato_tecnico', 'contato_administrativo',)
        }),
        (_('Alterações'), {
            'fields': ('data_alteracao', 'data_desativacao',
                       'motivo_desativacao',)
        }))
    readonly_fields = ('casa_legislativa', 'data_ativacao', 'data_alteracao')
    list_filter = (
        'tipo_servico',
        'hospedagem_interlegis',
        ServicoAtivoFilter,
        DataUtimoUsoFilter,
        ('casa_legislativa__gerentes_interlegis', GerentesInterlegisFilter),
        'casa_legislativa__municipio__uf',
    )
    list_display_links = []
    ordering = ('casa_legislativa__municipio__uf', 'casa_legislativa',
                'tipo_servico',)
    inlines = (LogServicoInline,)
    search_fields = ('casa_legislativa__search_text',)
    resource_class = ServicoExportResourse

    def get_codigo_interlegis(self, obj):
        return obj.casa_legislativa.codigo_interlegis
    get_codigo_interlegis.short_description = _('Código Interlegis')
    get_codigo_interlegis.admin_order_field = (
        'casa_legislativa__codigo_interlegis'
    )

    def get_uf(self, obj):
        return '%s' % (obj.casa_legislativa.municipio.uf)
    get_uf.short_description = _('UF')
    get_uf.admin_order_field = 'casa_legislativa__municipio__uf'

    def getUrl(self, obj):
        return mark_safe(f'<a href="{obj.url}" target="_blank">{obj.url}</a>')
    getUrl.short_description = _('Url')

    def get_link_erro(self, obj):
        if not obj.erro_atualizacao:
            return ""
        url = obj.url
        if url[-1] != '/':
            url += '/'
        if obj.tipo_servico.string_pesquisa:
            url += obj.tipo_servico.string_pesquisa.splitlines()[0].split(" ")[0]
        return mark_safe(
            f'<a href="{url}" target="_blank">{obj.erro_atualizacao}</a>'
        )
    get_link_erro.short_description = _("Erro na atualização")
    get_link_erro.admin_order_field = 'erro_atualizacao'

    # def adicionar_servicos(self, request, queryset):
    #     if 'carrinho_servicos' in request.session:
    #         q1 = len(request.session['carrinho_servicos'])
    #     else:
    #         q1 = 0
    #     adicionar_servicos_carrinho(request, queryset=queryset)
    #     q2 = len(request.session['carrinho_servicos'])
    #     quant = q2 - q1
    #     if quant:
    #         self.message_user(request, str(q2 - q1) + _(" Serviços adicionados no carrinho"))
    #     else:
    #         self.message_user(request, _("Os Serviços selecionados já foram adicionadas anteriormente"))
    #     return HttpResponseRedirect('.')
    # adicionar_servicos.short_description = _("Armazenar serviços no carrinho para exportar")

    def calcular_data_uso(self, request, queryset):
        for servico in queryset:
            servico.atualiza_data_uso()
        self.message_user(request, _("Atualização concluída. Os sites que não "
                                     "responderam foram deixados com a data "
                                     "em branco"))
        return HttpResponseRedirect('.')
    calcular_data_uso.short_description = _(
        "Atualizar a data do último uso do(s) serviço(s)"
    )

    def lookup_allowed(self, lookup, value):
        return super(ServicoAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['casa_legislativa__municipio__uf__codigo_ibge__exact', ]

    def add_view(self, request, form_url='', extra_context=None):
        id_casa = request.GET.get('id_casa', None)

        if not id_casa:
            raise Http404

        return super(ServicoAdmin, self).add_view(request, form_url,
                                                  extra_context=extra_context)

    def response_add(self, request, obj):
        opts = obj._meta
        msg = (_('The %(name)s "%(obj)s" was added successfully.') %
               {'name': force_str(opts.verbose_name),
                'obj': force_str(obj)}
        )

        if "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_str(opts.verbose_name)))
            return HttpResponseRedirect(request.path + '?id_casa=%s' % (obj.casa_legislativa.id,))
        elif "_save" in request.POST:
            self.message_user(request, msg)
            return HttpResponseRedirect(reverse('admin:servicos_casaatendida_change', args=[obj.casa_legislativa.id]))

        return super(ServicoAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        opts = obj._meta
        msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_str(opts.verbose_name), 'obj': force_str(obj)}

        if "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_str(opts.verbose_name)))
            return HttpResponseRedirect("../add/?id_casa=%s" % (obj.casa_legislativa.id,))
        elif "_save" in request.POST:
            self.message_user(request, msg)
            return HttpResponseRedirect(reverse('admin:servicos_casaatendida_change', args=[obj.casa_legislativa.id]))

        return super(ServicoAdmin, self).response_change(request, obj)

    def save_form(self, request, form, change):
        obj = super(ServicoAdmin, self).save_form(request, form, change)
        if not change:
            id_casa = request.GET.get('id_casa', None)
            if not id_casa:
                raise Http404
            obj.casa_legislativa = Orgao.objects.get(pk=id_casa)
        return obj

    def changelist_view(self, request, extra_context=None):
        from sigi.apps.convenios.views import normaliza_data
        request.GET._mutable = True
        normaliza_data(request.GET, 'data_ativacao__gte')
        normaliza_data(request.GET, 'data_ativacao__lte')
        request.GET._mutable = False

        return super(ServicoAdmin, self).changelist_view(
            request,
            extra_context={'query_str': '?' + request.META['QUERY_STRING']}
        )

    # def adicionar_servicos(self, request, queryset):
    #     if 'carrinho_servicos' in request.session:
    #         q1 = len(request.session['carrinho_servicos'])
    #     else:
    #         q1 = 0
    #     adicionar_servicos_carrinho(request, queryset=queryset)
    #     q2 = len(request.session['carrinho_servicos'])
    #     quant = q2 - q1
    #     if quant:
    #         self.message_user(request, str(q2 - q1) + _(" Convênios adicionados no carrinho"))
    #     else:
    #         self.message_user(request, _("Os Convênios selecionados já foram adicionadas anteriormente"))
    #     return HttpResponseRedirect('.')
    # adicionar_servicos.short_description = _("Armazenar Serviços no carrinho para exportar")

class ContatosInline(FuncionariosInline):
    can_delete = False  # Equipe do SEIT não pode excluir pessoas de contato
    # SEIT see all contacts, including President
    def get_queryset(self, request):
        return self.model.objects.all()

    def get_queryset(self, request):
        return (self.model.objects.exclude(desativado=True)
        .extra(select={'ult_null': 'ult_alteracao is null'})
        .order_by('ult_null', '-ult_alteracao')
            # A função extra foi usada para quando existir um registro com o campo igual a null não aparecer na frente dos mais novos
        )

@admin.register(CasaAtendida)
class CasaAtendidaAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('codigo_interlegis', 'nome', 'get_servicos',)
    ordering = ['nome']
    fieldsets = (
        ('Casa Legislativa', {
            'fields': (('codigo_interlegis', 'nome'), ('logradouro', 'bairro',
                                                       'municipio', 'cep'),
                       ('email', 'pagina_web'))
        }),)
    readonly_fields = ('nome', 'logradouro', 'bairro', 'municipio', 'cep')
    inlines = (ContatosInline,)
    list_filter = ('tipo', 'servico__tipo_servico', 'municipio__uf__nome',
                   'servico__casa_legislativa__convenio__projeto')
    search_fields = ('search_text', 'cnpj', 'bairro', 'logradouro',
                     'cep', 'municipio__nome', 'municipio__uf__nome',
                     'municipio__codigo_ibge', 'pagina_web', 'observacoes')

    def get_servicos(self, obj):
        result = [
            f"{servico.tipo_servico.nome} ({servico.status_servico}). "
            f"Contato: {servico.contato_administrativo.nome}"
            for servico in obj.servico_set.all()
        ]

        return mark_safe("<ul><li>" + "</li><li>".join(result) + "</li></ul>")
    get_servicos.short_description = _("Serviços")

    def lookup_allowed(self, lookup, value):
        return super(CasaAtendidaAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['municipio__uf__codigo_ibge__exact', 'servico__tipo_servico__id__exact', ]

    def change_view(self, request, object_id, extra_context=None):
        # Se a Casa ainda não é atendida, gerar o código interlegis para ela
        # Assim ela passa a ser uma casa atendida
        casa = Orgao.objects.get(id=object_id)

        if casa.codigo_interlegis == '':
            casa.gerarCodigoInterlegis()

        return super(CasaAtendidaAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def has_add_permission(self, request):
        return False  # Nunca é permitido inserir uma nova Casa Legislativa por aqui

    def has_delete_permission(self, request, obj=None):
        return False  # Nunca deletar casas por aqui
