# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.servicos.models import Servico, LogServico, CasaAtendida, TipoServico
#from sigi.apps.casas.models import Funcionario
from sigi.apps.casas.admin import FuncionariosInline
from django.http import Http404, HttpResponseRedirect
from django.forms.models import ModelForm
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from apps.casas.models import CasaLegislativa

#---------------- inlines ---------------------
class LogServicoInline(admin.StackedInline):
    model = LogServico
    Fieldset = ((None, {'fields': (('data', 'descricao'), 'log')}))
    extra = 1

# --------------- forms -----------------------
class ServicoFormAdmin(ModelForm):
    class Meta:
        model = Servico
        
    def __init__(self, *args, **kwargs):
        super(ServicoFormAdmin, self).__init__(*args, **kwargs)
        
        self.fields['contato_tecnico'].choices = ()
        self.fields['contato_administrativo'].choices = ()
        
        if self.instance.casa_legislativa_id:
            id_casa = self.instance.casa_legislativa_id
        elif kwargs.has_key('initial') and kwargs['initial'].has_key('id_casa'):
            id_casa = kwargs['initial']['id_casa']
            self.instance.casa_legislativa_id = id_casa
        else:
            id_casa = None
            
        if id_casa:
            casa = CasaAtendida.objects.get(pk=id_casa)
            contatos = [(f.id, unicode(f)) for f in casa.funcionario_set.all()] 
            self.fields['contato_tecnico'].choices = contatos
            self.fields['contato_administrativo'].choices = contatos
        
#---------------- admins ----------------------
class TipoServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sigla', 'nome', 'qtde_casas_atendidas', )
    ordering = ['id']
    
class ServicoAdmin(admin.ModelAdmin):
    form = ServicoFormAdmin
    list_display = ('casa_legislativa', 'tipo_servico', 'hospedagem_interlegis', 'data_ativacao', 'data_desativacao',)
    fieldsets = (( None, {
                    'fields': ('casa_legislativa', 'data_ativacao',)
                 }),
                 ( 'Serviço', {
                    'fields': ('tipo_servico', ('url', 'hospedagem_interlegis'), ('nome_servidor', 'porta_servico', 'senha_inicial'),)
                 }),
                 ( 'Contatos', {
                    'fields': ('contato_tecnico', 'contato_administrativo',)
                 }),
                 ( 'Alterações', {
                    'fields': ('data_alteracao', 'data_desativacao', 'motivo_desativacao',)
                }))
    readonly_fields = ('casa_legislativa', 'data_ativacao', 'data_alteracao')

    inlines = (LogServicoInline,)
    
    def add_view(self, request, form_url='', extra_context=None):
        id_casa = request.GET.get('id_casa', None)

        if not id_casa:
            raise Http404
        
        return super(ServicoAdmin, self).add_view(request, form_url, extra_context=extra_context)
    
    def response_add(self, request, obj):
        opts = obj._meta
        msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        
        if request.POST.has_key("_addanother"):
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
            return HttpResponseRedirect(request.path + '?id_casa=%s' % (obj.casa_legislativa.id,))
        elif request.POST.has_key("_save"):
            self.message_user(request, msg)
            return HttpResponseRedirect(reverse('admin:servicos_casaatendida_change', args=[obj.casa_legislativa.id]))
        
        return super(ServicoAdmin, self).response_add(request, obj)    
        
    def response_change(self, request, obj):
        opts = obj._meta
        msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        
        if request.POST.has_key("_addanother"):
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
            return HttpResponseRedirect("../add/?id_casa=%s" % (obj.casa_legislativa.id,))
        elif request.POST.has_key("_save"):
            self.message_user(request, msg)
            return HttpResponseRedirect(reverse('admin:servicos_casaatendida_change', args=[obj.casa_legislativa.id]))
        
        return super(ServicoAdmin, self).response_change(request, obj)
    
    def save_form(self, request, form, change):
        obj = super( ServicoAdmin, self).save_form(request, form, change)
        
        if not change:
            id_casa = request.GET.get('id_casa', None)

            if not id_casa:            
                raise Http404

            obj.casa_legislativa = CasaAtendida.objects.get(pk=id_casa)

        return obj

class ContatosInline(FuncionariosInline):
    can_delete = False # Equipe do SEIT não pode excluir pessoas de contato
                
class CasaAtendidaAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('codigo_interlegis', 'nome', 'servicos',)
    ordering = ['nome']
    fieldsets = (
                 ('Casa legislativa', {
                    'fields': (('codigo_interlegis', 'nome'),  ('logradouro', 'bairro', 'municipio', 'cep'), ('email', 'pagina_web'))
                    })
                ,)
    readonly_fields = ('nome',  'logradouro', 'bairro', 'municipio', 'cep')
    inlines = (ContatosInline,) 
    list_filter = ('tipo', 'municipio', )
    search_fields = ('search_text','cnpj', 'bairro', 'logradouro',
                     'cep', 'municipio__nome', 'municipio__uf__nome',
                     'municipio__codigo_ibge', 'pagina_web', 'observacoes')
    
    def lookup_allowed(self, lookup, value):
        return super(CasaAtendidaAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['municipio__uf__codigo_ibge__exact']

    def change_view(self, request, object_id, extra_context=None):
        # Se a Casa ainda não é atendida, gerar o código interlegis para ela
        # Assim ela passa a ser uma casa atendida
        casa = CasaLegislativa.objects.get(id=object_id)

        if casa.codigo_interlegis == '':
            casa.gerarCodigoInterlegis()
            
        return super(CasaAtendidaAdmin, self).change_view(request, object_id, extra_context=extra_context)
    
    def has_add_permission(self, request):
        return False # Nunca é permitido inserir uma nova Casa Legislativa por aqui
    
    def has_delete_permission(self, request, obj=None):
        return False # Nunca deletar casas por aqui