# -*- coding: utf-8 -*-
#
# sigi.apps.contatos.management.commands.importa_mesomicro
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
import os

from django.core.management.base import BaseCommand, CommandError

from sigi.apps.contatos.models import (Mesorregiao, Microrregiao, Municipio,
                                       UnidadeFederativa)


class Command(BaseCommand):
    args = u"data_file.csv"
    help = u"""Importa arquivo do IBGE para preencher as tabelas de meso e microrregiões para os municípios.
    
    A primeira linha do arquivo deve possuir um cabeçalho com os seguintes campos obrigatórios:
        - cod_uf            : Código IBGE da Unidade da Federação
        - cod_mesorregiao   : Código IBGE da mesorregião
        - nome_mesorregiao  : Nome da mesorregião
        - cod_microrregiao  : Código IBGE da microrregião
        - nome_microrregiao : Nome da microrregião
        - cod_municipio     : Código IBGE do município
        
    * Os nomes dos campos devem ser grafados exatamente como descrito."""
    
    campos = {'cod_uf', 'cod_mesorregiao', 'nome_mesorregiao', 'cod_microrregiao',
              'nome_microrregiao', 'cod_municipio'}
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError(u"Informe UM arquivo csv a importar")
        
        file_name = args[0]
        
        if not os.path.isfile(file_name):
            raise CommandError(u"Arquivo %s não encontrado" % [file_name,])
        
        with open(file_name, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if not self.campos.issubset(reader.fieldnames):
                raise CommandError(u"O arquivo não possui todos os campos obrigatórios")
            
            erros = 0
            
            for reg in reader:
                try:
                    uf = UnidadeFederativa.objects.get(codigo_ibge=reg['cod_uf'])
                except UnidadeFederativa.DoesNotExist:
                    self.stdout.write(u"(Linha %s): não existe UF com código IBGE '%s'" %
                                      (reader.line_num, reg['cod_uf'],))
                    erros = erros + 1
                    continue
            
                try:
                    municipio = Municipio.objects.get(codigo_ibge=reg['cod_municipio'])
                except Municipio.DoesNotExist:
                    self.stdout.write(u"(Linha %s): não existe Município com código IBGE '%s'" % 
                                      (reader.line_num, reg['cod_municipio'],))
                    erros = erros + 1
                    continue
                
                cod_meso = reg['cod_uf'] + reg['cod_mesorregiao']
                cod_micro = cod_meso + reg['cod_microrregiao']
                
                if Mesorregiao.objects.filter(codigo_ibge=cod_meso).exists():
                    meso = Mesorregiao.objects.get(codigo_ibge=cod_meso)
                else:
                    meso = Mesorregiao(codigo_ibge=cod_meso, uf=uf, nome=reg['nome_mesorregiao'])
                meso.nome = reg['nome_mesorregiao']
                meso.save()
                
                if Microrregiao.objects.filter(codigo_ibge=cod_micro).exists():
                    micro = Microrregiao.objects.get(codigo_ibge=cod_micro)
                else:
                    micro = Microrregiao(codigo_ibge=cod_micro, mesorregiao=meso, nome=reg['nome_microrregiao'])
                micro.nome = reg['nome_microrregiao']
                micro.save()
                
                municipio.microrregiao = micro
                municipio.save()
            
            self.stdout.write(u"Importação concluída. %s erros em %s linhas" % (erros, reader.line_num,))
