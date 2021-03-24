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

from django.core.management.base import BaseCommand, CommandError
from sigi.apps.convenios.models import Projeto, Convenio

class Command(BaseCommand):
    help = u"""Define a duração de todos os ACT para 60 meses.
    * A sigla do Projeto precisa ser ACT;
    * O campo duracao precisa estar em branco.
    """

    def handle(self, *args, **options):
        self.stdout.write(u"Atualizando ACTs... ")
        act = Projeto.objects.get(sigla='ACT')
        for conv in Convenio.objects.filter(projeto=act, duracao=None):
            conv.duracao = 60
            conv.save()
            self.stdout.write(u"\tACT {sigad} da Casa {casa} atualizado".format(
                sigad=conv.num_processo_sf, casa=conv.casa_legislativa.nome
            ))
        self.stdout.write(u"Pronto!")
