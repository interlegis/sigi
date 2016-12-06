# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import escape, escapejs
from django.utils.translation import ugettext as _

from sigi.apps.contatos.models import Telefone
from sigi.apps.parlamentares.models import (Cargo, Coligacao,
                                            ComposicaoColigacao, Legislatura,
                                            Mandato, MembroMesaDiretora,
                                            MesaDiretora, Parlamentar, Partido,
                                            SessaoLegislativa)
from sigi.apps.parlamentares.views import adicionar_parlamentar_carrinho
from sigi.apps.utils.base_admin import BaseModelAdmin
from sigi.apps.utils.filters import AlphabeticFilter


class MandatosInline(admin.TabularInline):
    model = Mandato
    extra = 1
    raw_id_fields = ('legislatura', 'partido')


class TelefonesInline(GenericTabularInline):
    model = Telefone
    extra = 2


class PartidoAdmin(BaseModelAdmin):
    list_display = ('nome', 'sigla')
    list_display_links = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')


class ParlamentarNomeCompletoFilter(AlphabeticFilter):
    title = _(u'Inicial do Nome Completo')
    parameter_name = 'nome_completo'


class ParlamentarAdmin(BaseModelAdmin):
    inlines = (TelefonesInline, MandatosInline)
    list_display = ('nome_completo', 'nome_parlamentar', 'sexo')
    list_display_links = ('nome_completo', 'nome_parlamentar')
    list_filter = (ParlamentarNomeCompletoFilter, )
    actions = ['adiciona_parlamentar', ]
    fieldsets = (
        (None, {
            'fields': ('nome_completo', 'nome_parlamentar', 'sexo'),
        }),
        #        (_(u'Endereço'), {
        #            'fields': ('logradouro', 'bairro', 'municipio', 'cep'),
        #        }),
        (_(u'Outras informações'), {
            'fields': ('data_nascimento', 'email', 'pagina_web', 'foto'),
        }),
    )
    radio_fields = {'sexo': admin.VERTICAL}
#    raw_id_fields = ('municipio',)
    search_fields = ('nome_completo', 'nome_parlamentar', 'email',
                     'pagina_web',)

    def adiciona_parlamentar(self, request, queryset):
        if 'carrinho_parlametar' in request.session:
            q1 = len(request.session['carrinho_parlamentar'])
        else:
            q1 = 0
        adicionar_parlamentar_carrinho(request, queryset=queryset)
        q2 = len(request.session['carrinho_parlamentar'])
        quant = q2 - q1
        if quant:
            self.message_user(request, _(u"%s Parlamentares adicionados no carrinho") % (quant))
        else:
            self.message_user(request, _(u"Os parlamentares selecionadas já foram adicionadas anteriormente"))
        return HttpResponseRedirect('.')

    adiciona_parlamentar.short_description = _(u"Armazenar parlamentar no carrinho para exportar")


class MandatoAdmin(BaseModelAdmin):
    list_display = ('parlamentar', 'legislatura', 'partido',
                    'inicio_mandato', 'fim_mandato', 'is_afastado')
    list_filter = ('is_afastado', 'partido')
    search_fields = ('legislatura__numero', 'parlamentar__nome_completo',
                     'parlamentar__nome_parlamentar', 'partido__nome',
                     'partido__sigla')
    raw_id_fields = ('parlamentar', 'legislatura', 'partido')
#    radio_fields = {'suplencia': admin.VERTICAL}


class MandatoInline(admin.TabularInline):
    model = Mandato
    raw_id_fields = ['parlamentar', ]


class LegislaturaAdmin(BaseModelAdmin):
    date_hierarchy = 'data_inicio'
    list_display = ('numero', 'casa_legislativa', 'uf', 'data_inicio', 'data_fim', 'data_eleicao', 'total_parlamentares')
    raw_id_fields = ('casa_legislativa',)
    list_display_links = ('numero',)
    list_filter = ('casa_legislativa__municipio__uf', )
    search_fields = ('casa_legislativa__nome', 'casa_legislativa__municipio__nome')
    inlines = (MandatoInline,)

    def uf(self, obj):
        return obj.casa_legislativa.municipio.uf.sigla
    uf.short_description = _(u'UF')
    uf.admin_order_field = 'casa_legislativa__municipio__uf'

    def lookup_allowed(self, lookup, value):
        return super(LegislaturaAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['casa_legislativa__municipio__uf__codigo_ibge__exact']

    def response_change(self, request, obj):
        response = super(LegislaturaAdmin, self).response_change(request, obj)
        if "_popup" in request.POST:
            response = HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %
                                    # escape() calls force_unicode.
                                    (escape(obj.pk), escapejs(obj)))
        return response


class ColigacaoAdmin(BaseModelAdmin):
    list_display = ('nome', 'legislatura', 'numero_votos')
    list_display_links = ('nome',)
    raw_id_fields = ('legislatura',)
    search_fields = ('nome', 'legislatura__numero')


class ComposicaoColigacaoAdmin(BaseModelAdmin):
    list_display = ('coligacao', 'partido')
    list_display_links = ('coligacao', 'partido')
    list_filter = ('partido',)
    raw_id_fields = ('coligacao', 'partido')
    search_fields = ('coligacao__nome', 'partido__nome', 'partido__sigla')


class SessaoLegislativaAdmin(BaseModelAdmin):
    list_display = ('numero', 'mesa_diretora', 'legislatura', 'tipo',
                    'data_inicio', 'data_fim')
    list_display_links = ('numero',)
    list_filter = ('tipo',)
    fieldsets = (
        (None, {
            'fields': ('numero', 'mesa_diretora', 'legislatura', 'tipo')
        }),
        (None, {
            'fields': (('data_inicio', 'data_fim'),
                       ('data_inicio_intervalo', 'data_fim_intervalo'))
        }),
    )
    radio_fields = {'tipo': admin.VERTICAL}
    raw_id_fields = ('mesa_diretora', 'legislatura')
    search_fields = ('numero', 'mesa_diretora__casa_legislativa__nome')


class CargoAdmin(BaseModelAdmin):
    list_display = ('descricao',)
    search_fields = ('descricao',)


class MembroMesaDiretoraInline(admin.TabularInline):
    model = MembroMesaDiretora
    max_num = 11
    extra = 4
    raw_id_fields = ('parlamentar', 'cargo')


class MembroMesaDiretoraAdmin(BaseModelAdmin):
    list_display = ('parlamentar', 'cargo', 'mesa_diretora')
    list_display_links = ('parlamentar',)
    list_filter = ('cargo',)
    raw_id_fields = ('parlamentar', 'cargo', 'mesa_diretora')
    search_fields = ('cargo__descricao', 'parlamentar__nome_completo',
                     'parlamentar__nome_parlamentar',
                     'mesa_diretora__casa_legislativa__nome')


class MesaDiretoraAdmin(BaseModelAdmin):
    inlines = (MembroMesaDiretoraInline,)
    raw_id_fields = ('casa_legislativa',)
    list_display = ('id', 'casa_legislativa')
    search_fields = ('casa_legislativa__nome',)


admin.site.register(Partido, PartidoAdmin)
admin.site.register(Parlamentar, ParlamentarAdmin)
admin.site.register(Mandato, MandatoAdmin)
admin.site.register(Legislatura, LegislaturaAdmin)
admin.site.register(Coligacao, ColigacaoAdmin)
admin.site.register(ComposicaoColigacao, ComposicaoColigacaoAdmin)
admin.site.register(SessaoLegislativa, SessaoLegislativaAdmin)
admin.site.register(MesaDiretora, MesaDiretoraAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(MembroMesaDiretora, MembroMesaDiretoraAdmin)
