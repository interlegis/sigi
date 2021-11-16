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
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from sigi.apps.eventos.models import TipoEvento, Funcao, Evento, Equipe, Convite
from sigi.apps.eventos.views import adicionar_eventos_carrinho

class EventoAdminForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ('tipo_evento', 'nome', 'descricao', 'virtual', 'solicitante',
                  'data_inicio', 'data_termino', 'carga_horaria',
                  'casa_anfitria', 'municipio', 'local', 'publico_alvo',
                  'status', 'data_cancelamento', 'motivo_cancelamento', )

    def clean(self):
        cleaned_data = super(EventoAdminForm, self).clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_termino = cleaned_data.get("data_termino")

        if data_inicio > data_termino:
            raise forms.ValidationError(
                _(u"Data término deve ser posterior à data inicio"),
                code="invalid_period"
            )

@admin.register(TipoEvento)
class TipoEventAdmin(admin.ModelAdmin):
    search_fields = ('nome',)

@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao',)
    search_fields = ('nome', 'descricao',)

class EquipeInline(admin.TabularInline):
    model = Equipe

class ConviteInline(admin.TabularInline):
    model = Convite
    raw_id_fields = ('casa',)

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    form = EventoAdminForm
    date_hierarchy = 'data_inicio'
    list_display = ('nome', 'tipo_evento', 'status', 'data_inicio',
                    'data_termino', 'municipio', 'solicitante')
    list_filter = ('status', 'tipo_evento', 'virtual', 'municipio__uf',
                   'solicitante')
    raw_id_fields = ('casa_anfitria', 'municipio',)
    search_fields = ('nome', 'tipo_evento__nome', 'casa_anfitria__search_text',
                     'municipio__search_text', 'solicitante')
    inlines = (EquipeInline, ConviteInline)
    actions = ['adicionar_eventos', ]

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
