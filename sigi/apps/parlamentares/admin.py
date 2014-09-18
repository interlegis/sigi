# -*- coding: utf-8 -*-
import string

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.http import HttpResponse, HttpResponseRedirect

from sigi.apps.contatos.models import Telefone
from sigi.apps.parlamentares.models import Partido, Parlamentar, Mandato
from sigi.apps.parlamentares.views import adicionar_parlamentar_carrinho
from sigi.apps.utils.alphabetic_filter import AlphabeticFilter


class MandatosInline(admin.TabularInline):
    model = Mandato
    extra = 1
    raw_id_fields = ('legislatura', 'partido')


class TelefonesInline(generic.GenericTabularInline):
    model = Telefone
    extra = 2


class PartidoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    list_display_links = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')


class ParlamentarNomeCompletoFilter(AlphabeticFilter):
    title = 'Nome Completo do Parlamentar'
    parameter_name = 'nome_completo'


class ParlamentarAdmin(admin.ModelAdmin):
    inlines = (TelefonesInline, MandatosInline)
    list_display = ('nome_completo', 'nome_parlamentar', 'sexo')
    list_display_links = ('nome_completo', 'nome_parlamentar')
    list_filter = ('nome_parlamentar', ParlamentarNomeCompletoFilter)
    actions = ['adiciona_parlamentar', ]
    fieldsets = (
        (None, {
            'fields': ('nome_completo', 'nome_parlamentar', 'sexo'),
        }),
        #        ('Endereço', {
        #            'fields': ('logradouro', 'bairro', 'municipio', 'cep'),
        #        }),
        ('Outras informações', {
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
            self.message_user(request, "%s Parlamentares adicionados no carrinho" % (quant))
        else:
            self.message_user(request, "Os parlamentares selecionadas já foram adicionadas anteriormente")
        return HttpResponseRedirect('.')

    adiciona_parlamentar.short_description = u"Armazenar parlamentar no carrinho para exportar"


class MandatoAdmin(admin.ModelAdmin):
    list_display = ('parlamentar', 'legislatura', 'partido',
                    'inicio_mandato', 'fim_mandato', 'is_afastado')
    list_filter = ('is_afastado', 'partido')
    search_fields = ('legislatura__numero', 'parlamentar__nome_completo',
                     'parlamentar__nome_parlamentar', 'partido__nome',
                     'partido__sigla')
    raw_id_fields = ('parlamentar', 'legislatura', 'partido')
#    radio_fields = {'suplencia': admin.VERTICAL}


admin.site.register(Partido, PartidoAdmin)
admin.site.register(Parlamentar, ParlamentarAdmin)
admin.site.register(Mandato, MandatoAdmin)
