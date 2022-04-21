# -*- coding: utf-8 -*-
#
# sigi.apps.casas.management.commands.importa_gerentes
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
from sigi.apps.casas.models import Orgao
from sigi.apps.servidores.models import Servidor
from sigi.apps.contatos.models import Municipio


class Command(BaseCommand):
    args = "data_file.csv"
    help = """Importa dados de atribuição de gerencia de relacionamentos de um arquivo CSV.

    A primeira linha do arquivo deve possuir um cabeçalho com os seguintes campos obrigatórios:
        - cod_municipio : Código IBGE do município
        - user_id       : Nome de usuário (usado no login) do gerente de relacionamento da Casa

    * Os nomes dos campos devem ser grafados exatamente como descrito."""

    campos = {"cod_municipio", "user_id"}

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Informe UM arquivo csv a importar")

        file_name = args[0]

        if not os.path.isfile(file_name):
            raise CommandError(
                "Arquivo %s não encontrado"
                % [
                    file_name,
                ]
            )

        with open(file_name, "rb") as csvfile:
            reader = csv.DictReader(csvfile)

            if not self.campos.issubset(reader.fieldnames):
                raise CommandError(
                    "O arquivo não possui todos os campos obrigatórios"
                )

            Orgao.gerentes_interlegis.through.objects.all().delete()

            erros = 0

            for reg in reader:
                try:
                    municipio = Municipio.objects.get(
                        codigo_ibge=reg["cod_municipio"]
                    )
                except Municipio.DoesNotExist:
                    self.stdout.write(
                        "{linha}: não existe Município com "
                        "código IBGE {ibge}'".format(
                            linha=reader.line_num, ibge=reg["cod_municipio"]
                        )
                    )
                    erros = erros + 1
                    continue

                try:
                    gerente = Servidor.objects.get(
                        user__username=reg["user_id"]
                    )
                except Servidor.DoesNotExist:
                    self.stdout.write(
                        "({linha}): não existe Servidor com "
                        "userid {userid}".format(
                            linha=reader.line_num, userid=reg["user_id"]
                        )
                    )
                    erros = erros + 1
                    continue

                for casa in municipio.orgao_set.filter(
                    tipo__sigla__in=["AL", "CM"]
                ):
                    casa.gerentes_interlegis.add(gerente)
                    casa.save()

            self.stdout.write(
                "Importação concluída. {erros} erros em {linhas}"
                " linhas".format(erros=erros, linhas=reader.line_num)
            )
