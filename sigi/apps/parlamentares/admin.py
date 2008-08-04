# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.parlamentares.models import Partido, Parlamentar, Mandato

class PartidoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    list_display_links = ('nome', 'sigla')

class ParlamentarAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'nome_parlamentar', 'sexo')
    list_display_links = ('nome_completo', 'nome_parlamentar')
    list_filter = ('sexo',)
    radio_fields = {'sexo': admin.VERTICAL}

class MandatoAdmin(admin.ModelAdmin):
    list_display = ('parlamentar', 'legislatura', 'partido',
                    'inicio_mandato', 'fim_mandato', 'is_afastado')
    list_filter = ('is_afastado', 'partido', 'suplencia')
    radio_fields = {'suplencia': admin.VERTICAL}

admin.site.register(Partido, PartidoAdmin)
admin.site.register(Parlamentar, ParlamentarAdmin)
admin.site.register(Mandato, MandatoAdmin)
