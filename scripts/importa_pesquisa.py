# -*- coding: utf-8 -*-
#
# importa_pesquisa
#
# Copyright (c) 2015 by Interlegis
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import csv
import urlparse
from datetime import datetime

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.servidores.models import Servidor


def importa(file_list):
    ''' Este script importa dados de um arquivo CSV e dá carga no model casas.CasaLegislativa

        O arquivo CSV esperado tem um cabeçalho de campos na primeira linha, com os seguintes campos:
        
        Indicação de data e hora,Pesquisador,Câmara,Possui portal,Portal Modelo,URL,Observações
        
        Indicação de data e hora: Uma string datetime no formato %d/%m/%y %H:%M
        Pesquisador: O nome do servidor que realizou a pesquisa, conforme cadastrado no SIGI
        Câmara: A sigla da UF seguida de um espaço, seguido de um caracter - seguido de um espaço seguido do nome do município,
                exemplo: MG - Montes Claros
        Possui portal: Deve constar "sim" ou "não" indicando se a casa possui ou não portal.
        Portal Modelo: Deve constar "sim" ou "não" indicando se o portal da casa é o portal modelo ou não.
        URL: Deve conter a URL do portal da Casa. Opcionalmente pode ter alguma observação do pesquisador
        Observações: Deve conter as observações do pesquisador, caso existam.''' 
    
    for filename in file_list:
        print 'Importando '+filename+'.csv'
        with open(filename+'.csv', 'rb') as infile:
            with open(filename+'.out', 'wb') as outfile:
                indata = csv.reader(infile, delimiter=',', quotechar='"')
                outdata = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        
                head = next(indata)
                head.append('Erros encontrados')
                outdata.writerow(head)
        
                for row in indata:
                    data = row[0].strip()
                    pesquisador = row[1].strip()
                    uf_cidade = row[2].strip()
                    tem_portal = row[3].strip()
                    pmodelo = row[4].strip()
                    url = row[5].strip()
                    obs = row[6].strip()
            
                    if data == '':
                        data = None
                    else:
                        data = datetime.strptime(data, '%d/%m/%y %H:%M')
        
                    uf = uf_cidade[:2]
                    cidade = uf_cidade[5:]
        
                    if tem_portal.lower() == 'não':
                        inclusao = CasaLegislativa.INCLUSAO_DIGITAL_CHOICES[1][0]
                    elif pmodelo.lower() == 'não':
                        inclusao = CasaLegislativa.INCLUSAO_DIGITAL_CHOICES[3][0]
                    else:
                        inclusao = CasaLegislativa.INCLUSAO_DIGITAL_CHOICES[2][0]
        
                    l = url.splitlines()
                    url = ''
            
                    for s in l:
                        p = urlparse.urlparse(s)
                        if p.netloc:
                            url = s
                        else:
                            obs = obs + '\n' + s
                    
                    if pesquisador == '':
                        servidor = None
                    else:
                        servidor = Servidor.objects.filter(nome_completo__iexact=pesquisador)
                        cc = servidor.count()
                        if cc == 0:
                            row.append('Não encontrado servidor com este nome')
                            outdata.writerow(row)
                            continue
                        else:
                            servidor = servidor[0]
                    
                    casa = CasaLegislativa.objects.filter(tipo_id=1, municipio__uf__sigla=uf, municipio__nome__iexact=cidade)
                    cc = casa.count()
                    if cc == 0:
                        row.append('Municipio nao foi encontrado')
                        outdata.writerow(row)
                        continue
                    elif cc > 1:
                        row.append('Existem %s casas legislativas nesta cidade')
                        outdata.writerow(row)
                        continue
                    else:
                        casa = casa[0]
                
                    casa.inclusao_digital = inclusao
                    casa.data_levantamento = data
                    casa.pesquisador = servidor
                    
                    if casa.pagina_web == '':
                        casa.pagina_web = url
                    else:
                        obs = url + '\n' + obs
                        
                    casa.obs_pesquisa = obs
                    casa.save()
                    
        print 'O arquivo '+filename+'.out foi criado com os registros que nao puderam ser importados'            
