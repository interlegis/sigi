# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from sigi.apps.casas.admin import FuncionariosInline
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.servicos.models import (CasaAtendida, LogServico, Servico,
                                       TipoServico)
from sigi.apps.utils.base_admin import BaseModelAdmin


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
            contatos = [(f.id, unicode(f)) for f in casa.funcionario_set.all()]
            self.fields['contato_tecnico'].choices = contatos
            self.fields['contato_administrativo'].choices = contatos


class TipoServicoAdmin(BaseModelAdmin):
    list_display = ('id', 'sigla', 'nome', 'qtde_casas_atendidas', )
    ordering = ['id']


class ServicoAdmin(BaseModelAdmin):
    form = ServicoFormAdmin
    actions = ['calcular_data_uso', ]
    list_display = ('casa_legislativa', 'get_codigo_interlegis', 'get_uf', 'tipo_servico', 'hospedagem_interlegis',
                    'data_ativacao', 'data_desativacao', 'getUrl', 'data_ultimo_uso', 'get_link_erro')
    fieldsets = ((None, {
        'fields': ('casa_legislativa', 'data_ativacao',)
    }),
        (_(u'Serviço'), {
            'fields': ('tipo_servico', ('url', 'hospedagem_interlegis'), ('nome_servidor', 'porta_servico', 'senha_inicial'),)
        }),
        (_(u'Contatos'), {
            'fields': ('contato_tecnico', 'contato_administrativo',)
        }),
        (_(u'Alterações'), {
            'fields': ('data_alteracao', 'data_desativacao', 'motivo_desativacao',)
        }))
    readonly_fields = ('casa_legislativa', 'data_ativacao', 'data_alteracao')
    list_filter = ('tipo_servico', 'hospedagem_interlegis', 'data_ultimo_uso', 'casa_legislativa__municipio__uf', )
    list_display_links = []
    ordering = ('casa_legislativa__municipio__uf', 'casa_legislativa', 'tipo_servico',)
    inlines = (LogServicoInline,)
    search_fields = ('casa_legislativa__search_text',)

    def get_codigo_interlegis(self, obj):
        return obj.casa_legislativa.codigo_interlegis
    get_codigo_interlegis.short_description = _(u'Código Interlegis')
    get_codigo_interlegis.admin_order_field = 'casa_legislativa__codigo_interlegis'

    def get_uf(self, obj):
        return u'%s' % (obj.casa_legislativa.municipio.uf)
    get_uf.short_description = _(u'UF')
    get_uf.admin_order_field = 'casa_legislativa__municipio__uf'

    def getUrl(self, obj):
        return u'<a href="%s" target="_blank">%s</a>' % (obj.url, obj.url)
    getUrl.short_description = _(u'Url')
    getUrl.allow_tags = True

    def get_link_erro(self, obj):
        if not obj.erro_atualizacao:
            return u""
        url = obj.url
        if url[-1] != '/':
            url += '/'
        url += obj.tipo_servico.string_pesquisa
        return u'<a href="%s" target="_blank">%s</a>' % (url, obj.erro_atualizacao)
    get_link_erro.allow_tags = True
    get_link_erro.short_description = _(u"Erro na atualização")
    get_link_erro.admin_order_field = 'erro_atualizacao'

    def calcular_data_uso(self, request, queryset):
        for servico in queryset:
            servico.atualiza_data_uso()
        self.message_user(request, _(u"Atualização concluída. Os sites que não responderam foram deixados com a data em branco"))
        return HttpResponseRedirect('.')
    calcular_data_uso.short_description = _(u"Atualizar a data do último uso do(s) serviço(s)")

    def get_actions(self, request):
        from collections import OrderedDict
        actions = [self.get_action(action) for action in self.actions]
        actions = filter(None, actions)
        actions.sort(lambda a, b: cmp(a[2].lower(), b[2].lower()))
        actions = OrderedDict([(name, (func, name, desc)) for func, name, desc in actions])
        return actions

    def lookup_allowed(self, lookup, value):
        return super(ServicoAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['casa_legislativa__municipio__uf__codigo_ibge__exact']

    def add_view(self, request, form_url='', extra_context=None):
        id_casa = request.GET.get('id_casa', None)

        if not id_casa:
            raise Http404

        return super(ServicoAdmin, self).add_view(request, form_url, extra_context=extra_context)

    def response_add(self, request, obj):
        opts = obj._meta
        msg = _(u'The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}

        if "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + (_(u"You may add another %s below.") % force_unicode(opts.verbose_name)))
            return HttpResponseRedirect(request.path + '?id_casa=%s' % (obj.casa_legislativa.id,))
        elif "_save" in request.POST:
            self.message_user(request, msg)
            return HttpResponseRedirect(reverse('admin:servicos_casaatendida_change', args=[obj.casa_legislativa.id]))

        return super(ServicoAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        opts = obj._meta
        msg = _(u'The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}

        if "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + (_(u"You may add another %s below.") % force_unicode(opts.verbose_name)))
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

            obj.casa_legislativa = CasaAtendida.objects.get(pk=id_casa)

        return obj


class ContatosInline(FuncionariosInline):
    can_delete = False  # Equipe do SEIT não pode excluir pessoas de contato


class CasaAtendidaAdmin(BaseModelAdmin):
    actions = None
    list_display = ('codigo_interlegis', 'nome', 'get_servicos',)
    ordering = ['nome']
    fieldsets = (
        ('Casa Legislativa', {
            'fields': (('codigo_interlegis', 'nome'), ('logradouro', 'bairro', 'municipio', 'cep'), ('email', 'pagina_web'))
        }),)
    readonly_fields = ('nome', 'logradouro', 'bairro', 'municipio', 'cep')
    inlines = (ContatosInline,)
    list_filter = ('tipo', 'servico__tipo_servico', 'municipio__uf__nome',
                   'servico__casa_legislativa__convenio__projeto')
    search_fields = ('search_text', 'cnpj', 'bairro', 'logradouro',
                     'cep', 'municipio__nome', 'municipio__uf__nome',
                     'municipio__codigo_ibge', 'pagina_web', 'observacoes')

    def get_servicos(self, obj):
        result = []
        for servico in obj.servico_set.all():
            result.append(u"%s (%s). %s: %s" % (
                servico.tipo_servico.nome,
                _(u'ativo') if servico.data_desativacao is None else _(u'desativado'),
                _(u'Contato'),
                servico.contato_administrativo.nome))

        return "<ul><li>" + "</li><li>".join(result) + "</li></ul>"
    get_servicos.allow_tags = True
    get_servicos.short_description = _(u"Serviços")

    def lookup_allowed(self, lookup, value):
        return super(CasaAtendidaAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['municipio__uf__codigo_ibge__exact', 'servico__tipo_servico__id__exact', ]

    def change_view(self, request, object_id, extra_context=None):
        # Se a Casa ainda não é atendida, gerar o código interlegis para ela
        # Assim ela passa a ser uma casa atendida
        casa = CasaLegislativa.objects.get(id=object_id)

        if casa.codigo_interlegis == '':
            casa.gerarCodigoInterlegis()

        return super(CasaAtendidaAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def has_add_permission(self, request):
        return False  # Nunca é permitido inserir uma nova Casa Legislativa por aqui

    def has_delete_permission(self, request, obj=None):
        return False  # Nunca deletar casas por aqui

admin.site.register(Servico, ServicoAdmin)
admin.site.register(TipoServico, TipoServicoAdmin)
admin.site.register(CasaAtendida, CasaAtendidaAdmin)
