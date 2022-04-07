# -*- coding: utf-8 -*-
#
# sigi.apps.eventos.admin
#
# Copyright (C) 2015  Interlegis
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from sigi.apps.eventos.models import (ModeloDeclaracao, Modulo, TipoEvento,
                                      Funcao, Evento, Equipe, Convite, Anexo)
from sigi.apps.eventos.views import adicionar_eventos_carrinho
from sigi.apps.eventos.forms import EventoAdminForm

class SigadFilter(admin.SimpleListFilter):
    title = _(u"Processo SIGAD")
    parameter_name = 'num_processo'

    def lookups(self, request, model_admin):
        return (
            ('empty', _(u"Sem proceesso SIGAD")),
            ('not_empty', _(u"Com processo SIGAD")),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            if self.value() == 'empty':
                queryset = queryset.filter(num_processo="")
            elif self.value() == 'not_empty':
                queryset = queryset.exclude(num_processo="")

        return queryset

@admin.register(TipoEvento)
class TipoEventAdmin(admin.ModelAdmin):
    search_fields = ('nome',)

@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao',)
    search_fields = ('nome', 'descricao',)

@admin.register(ModeloDeclaracao)
class ModeloDeclaracaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'formato')

class EquipeInline(admin.TabularInline):
    model = Equipe

class ConviteInline(admin.TabularInline):
    model = Convite
    raw_id_fields = ('casa',)

class ModuloInline(admin.TabularInline):
    model = Modulo

class AnexoInline(admin.TabularInline):
    model = Anexo
    exclude = ('data_pub',)

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    form = EventoAdminForm
    date_hierarchy = 'data_inicio'
    list_display = ('nome', 'tipo_evento', 'status', 'link_sigad',
                    'data_inicio', 'data_termino', 'municipio', 'solicitante',
                    'total_participantes',)
    list_filter = ('status', SigadFilter, 'tipo_evento',
                   'tipo_evento__categoria', 'virtual', 'municipio__uf',
                   'solicitante')
    raw_id_fields = ('casa_anfitria', 'municipio',)
    search_fields = ('nome', 'tipo_evento__nome', 'casa_anfitria__search_text',
                     'municipio__search_text', 'solicitante')
    inlines = (EquipeInline, ConviteInline, ModuloInline, AnexoInline)
    actions = ['adicionar_eventos', ]

    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return obj.get_sigad_url()
    link_sigad.short_description = _(u"número do processo SIGAD")
    link_sigad.allow_tags = True

    def adicionar_eventos(self, request, queryset):
        if 'carrinho_eventos' in request.session:
            q1 = len(request.session['carrinho_eventos'])
        else:
            q1 = 0
        response = adicionar_eventos_carrinho(request, queryset=queryset)
        q2 = len(request.session['carrinho_eventos'])
        quant = q2 - q1
        if quant:
            self.message_user(request, str(q2 - q1) + " " +
                              _(u"Eventos adicionados no carrinho"))
        else:
            self.message_user(request, _(u"Os Eventos selecionados "
                                         u"já foram adicionados anteriormente"))
        return HttpResponseRedirect('.')
    adicionar_eventos.short_description = _(u"Armazenar eventos no carrinho "
                                            u"para exportar")

    def lookup_allowed(self, lookup, value):
        return (super(EventoAdmin, self).lookup_allowed(lookup, value) or
                lookup in ['tipo_evento__nome__exact',
                            'tipo_evento__nome__contains'])
