# -*- coding: utf-8 -*-
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import escape

from sigi.apps.mesas.models import (Legislatura, Coligacao, ComposicaoColigacao,
                                    SessaoLegislativa, MesaDiretora, Cargo,
                                    MembroMesaDiretora)
from sigi.apps.parlamentares.models import Mandato


class MandatoInline(admin.TabularInline):
    model = Mandato
    raw_id_fields = ['parlamentar', ]


class LegislaturaAdmin(admin.ModelAdmin):
    date_hierarchy = 'data_inicio'
    list_display = ('numero', 'casa_legislativa', 'uf', 'data_inicio', 'data_fim', 'data_eleicao', 'total_parlamentares')
    raw_id_fields = ('casa_legislativa',)
    list_display_links = ('numero',)
    list_filter = ('casa_legislativa__municipio__uf', )
    search_fields = ('casa_legislativa__nome', 'casa_legislativa__municipio__nome')
    inlines = (MandatoInline,)

    def uf(self, obj):
        return obj.casa_legislativa.municipio.uf.sigla
    uf.short_description = 'UF'
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


class ColigacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'legislatura', 'numero_votos')
    list_display_links = ('nome',)
    raw_id_fields = ('legislatura',)
    search_fields = ('nome', 'legislatura__numero')


class ComposicaoColigacaoAdmin(admin.ModelAdmin):
    list_display = ('coligacao', 'partido')
    list_display_links = ('coligacao', 'partido')
    list_filter = ('partido',)
    raw_id_fields = ('coligacao', 'partido')
    search_fields = ('coligacao__nome', 'partido__nome', 'partido__sigla')


class SessaoLegislativaAdmin(admin.ModelAdmin):
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


class CargoAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    search_fields = ('descricao',)


class MembroMesaDiretoraInline(admin.TabularInline):
    model = MembroMesaDiretora
    max_num = 11
    extra = 4
    raw_id_fields = ('parlamentar', 'cargo')


class MembroMesaDiretoraAdmin(admin.ModelAdmin):
    list_display = ('parlamentar', 'cargo', 'mesa_diretora')
    list_display_links = ('parlamentar',)
    list_filter = ('cargo',)
    raw_id_fields = ('parlamentar', 'cargo', 'mesa_diretora')
    search_fields = ('cargo__descricao', 'parlamentar__nome_completo',
                     'parlamentar__nome_parlamentar',
                     'mesa_diretora__casa_legislativa__nome')


class MesaDiretoraAdmin(admin.ModelAdmin):
    inlines = (MembroMesaDiretoraInline,)
    raw_id_fields = ('casa_legislativa',)
    list_display = ('id', 'casa_legislativa')
    search_fields = ('casa_legislativa__nome',)

admin.site.register(Legislatura, LegislaturaAdmin)
admin.site.register(Coligacao, ColigacaoAdmin)
admin.site.register(ComposicaoColigacao, ComposicaoColigacaoAdmin)
admin.site.register(SessaoLegislativa, SessaoLegislativaAdmin)
admin.site.register(MesaDiretora, MesaDiretoraAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(MembroMesaDiretora, MembroMesaDiretoraAdmin)
