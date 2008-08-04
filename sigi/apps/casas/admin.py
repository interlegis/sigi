# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.casas.models import CasaLegislativa

class CasaLegislativaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'pagina_web')
    list_display_links = ('nome',)

admin.site.register(CasaLegislativa, CasaLegislativaAdmin)
