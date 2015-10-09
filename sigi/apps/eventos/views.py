# -*- coding: utf-8 -*-
#
# sigi.apps.eventos.views
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

import calendar
import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from sigi.apps.eventos.models import Evento

@login_required
def calendario(request):
    mes_pesquisa = int(request.GET.get('mes', datetime.date.today().month))
    ano_pesquisa = int(request.GET.get('ano', datetime.date.today().year))
    
    dia1 = datetime.date(ano_pesquisa, mes_pesquisa, 1)
    mes_anterior = dia1 - datetime.timedelta(days=1)
    mes_seguinte = dia1.replace(day=28) + datetime.timedelta(days=4) # Ugly hack
    mes_seguinte = mes_seguinte.replace(day=1)
    
    data = {'mes_pesquisa': mes_pesquisa, 'ano_pesquisa': ano_pesquisa}

    if Evento.objects.filter(data_inicio__year=mes_anterior.year, 
                             data_inicio__month=mes_anterior.month).exists():
        data['prev_button'] = {'mes': mes_anterior.month, 'ano': mes_anterior.year }
        
    if Evento.objects.filter(data_inicio__year=mes_seguinte.year, 
                             data_inicio__month=mes_seguinte.month).exists():
        data['next_button'] = {'mes': mes_seguinte.month, 'ano': mes_seguinte.year }
        
    c = calendar.Calendar(6)
    dates = reduce(lambda x,y: x+y, c.monthdatescalendar(ano_pesquisa, mes_pesquisa))
    
    eventos = []
    
    for evento in Evento.objects.filter(data_inicio__year=ano_pesquisa, 
                                        data_inicio__month=mes_pesquisa).order_by('data_inicio'):
        start = dates.index(evento.data_inicio)
        if not evento.data_termino in dates:
            lastday = dates[-1]
            while lastday < evento.data_termino:
                lastday = lastday + datetime.timedelta(days=1)
                dates.append(lastday)
        eventos.append({'evento': evento, 'start': start})

    # Calcula a distância dos eventos para as bordas do calendário
    for evento in eventos:
        end = dates.index(evento['evento'].data_termino)
        evento['duration'] = end-evento['start']+1
        evento['close'] = len(dates)-end-1

    # Agrupa os eventos em linhas para melhorar a visualização
    linhas = []
    
    for evento in eventos:
        encaixado = False
        for linha in linhas:
            sobrepoe = False
            for e in linha:
                if (((evento['evento'].data_inicio >= e['evento'].data_inicio) and 
                     (evento['evento'].data_inicio <= e['evento'].data_termino)) or
                    ((evento['evento'].data_termino >= e['evento'].data_inicio) and
                     (evento['evento'].data_termino <= e['evento'].data_termino))):
                    sobrepoe = True
                    break
            if not sobrepoe:
                # Adiona o evento em uma linha que ele não sobrepoe nenhum outro
                linha.append(evento)
                encaixado = True
                break
        if not encaixado:
            # Adiciona uma nova linha porque este evento não se encaixa em nenhuma existente
            linhas.append([evento])

    # Recalcula as distâncias dos eventos por linha para encaixar no calendário            
    for linha in linhas:
        anterior = None
        for evento in linha:
            if anterior is None:
                anterior = evento
                continue
            anterior['close'] = (evento['evento'].data_inicio - anterior['evento'].data_termino).days-1
            evento['start'] = 0
            anterior = evento

    data['dates'] = dates
    data['eventos'] = eventos
    data['linhas'] = linhas
    
    return render(request, 'eventos/calendario.html', data)