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
import csv
import datetime
import locale

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

from sigi.apps.eventos.models import Evento
from sigi.apps.servidores.models import Servidor
from sigi.shortcuts import render_to_pdf


@login_required
def calendario(request):
    mes_pesquisa = int(request.GET.get('mes', datetime.date.today().month))
    ano_pesquisa = int(request.GET.get('ano', datetime.date.today().year))
    formato = request.GET.get('fmt', 'html')
    
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
    
    if formato == 'pdf':
        return render_to_pdf('eventos/calendario_pdf.html', data )
    
    return render(request, 'eventos/calendario.html', data)

@login_required
def alocacao_equipe(request):
    ano_pesquisa = int(request.GET.get('ano', datetime.date.today().year))
    formato = request.GET.get('fmt', 'html')
    
    data = {'ano_pesquisa': ano_pesquisa}
    
    if Evento.objects.filter(data_inicio__year=ano_pesquisa-1).exists():
        data['prev_button'] = {'ano': ano_pesquisa - 1 }
        
    if Evento.objects.filter(data_inicio__year=ano_pesquisa+1).exists():
        data['next_button'] = {'ano': ano_pesquisa + 1 }
        
    dados = []
    
    for evento in Evento.objects.filter(data_inicio__year=ano_pesquisa).exclude(status='C').prefetch_related('equipe_set'):
        for p in evento.equipe_set.all():
            registro = None
            for r in dados:
                if r[0] == p.membro.pk:
                    registro = r
                    break
            if not registro:
                registro = [p.membro.pk, p.membro.nome_completo, [{'dias': 0, 'eventos': 0} for x in range(1,13)]]
                dados.append(registro)
                
            registro[2][evento.data_inicio.month-1]['dias'] += (evento.data_termino - evento.data_inicio).days + 1
            registro[2][evento.data_inicio.month-1]['eventos'] += 1
            
    dados.sort(lambda x, y: cmp(x[1], y[1]))
          
    lang = (translation.to_locale(translation.get_language())+'.utf8').encode()
    locale.setlocale(locale.LC_ALL, lang)
    meses = [calendar.month_name[m] for m in range(1,13)]
    
    linhas = [[_(u"Servidor")] + meses + ['total']]
    
    for r in dados:
        r[2].append(reduce(lambda x,y:{'dias': x['dias'] + y['dias'],
                                    'eventos': x['eventos'] + y['eventos']}, r[2]))
        linhas.append([r[1]] + 
                       [_(ungettext(u"%(dias)s dia", u"%(dias)s dias", d['dias']) + " em " +
                          ungettext(u"%(eventos)s evento", u"%(eventos)s eventos", d['eventos'])
                        ) % d if d['dias'] > 0 or d['eventos'] > 0 else '' for d in r[2]])
    
#     for registro in Servidor.objects.filter(equipe_evento__evento__data_inicio__year=ano_pesquisa).exclude(equipe_evento__evento__status='C').distinct():
#         dados = [{'dias': 0, 'eventos': 0} for x in range(1,13)]
#         for part in registro.equipe_evento.filter(evento__data_inicio__year=ano_pesquisa).exclude(evento__status='C'):
#             dados[part.evento.data_inicio.month-1]['dias'] +=  (part.evento.data_termino - 
#                                                                 part.evento.data_inicio).days + 1
#             dados[part.evento.data_inicio.month-1]['eventos'] += 1
#         dados.append([registro.nome_completo] + [_(ungettext(u"%(dias)s dia", u"%(dias)s dias", d['dias']) + " em " + ungettext(u"%(eventos)s evento", u"%(eventos)s eventos", d['eventos'])) % d if d['dias'] > 0 or d['eventos'] > 0 else '' for d in dados])
        
    data['linhas'] = linhas
    
    if formato == 'pdf':
        return render_to_pdf('eventos/alocacao_equipe_pdf.html', data)
    elif formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="alocacao_equipe_%s.csv"' % (ano_pesquisa,)
        writer = csv.writer(response)
        asc_list = [[s.encode('utf-8') if isinstance(s, unicode) else s for s in l] for l in linhas]
        writer.writerows(asc_list)
        return response
    elif formato == 'json':
        result = {'ano': ano_pesquisa,
                  'equipe': [{'pk': d[0],
                              'nome_completo': d[1],
                              'meses': {m[0]: m[1] for m in zip(meses+['total'], d[2])}
                             } for d in dados]}
        return JsonResponse(result)
    
    return render(request, 'eventos/alocacao_equipe.html', data)
