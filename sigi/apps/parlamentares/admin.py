# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from sigi.apps.contatos.models import Telefone
from sigi.apps.parlamentares.models import Partido, Parlamentar, Mandato

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

class ParlamentarAdmin(admin.ModelAdmin):
    inlines = (TelefonesInline, MandatosInline)
    list_display = ('nome_completo', 'nome_parlamentar', 'sexo')
    list_display_links = ('nome_completo', 'nome_parlamentar')
    list_filter = ('nome_completo', 'sexo')
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
