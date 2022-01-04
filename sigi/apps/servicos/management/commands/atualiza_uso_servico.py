# -*- coding: utf-8 -*-
#
# sigi.apps.servicos.management.commands.atualiza_uso_servico
#
# Copyright (c) 2012 by Interlegis
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
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from sigi.apps.servicos.models import Servico


class Command(BaseCommand):
    help = _(u'Atualiza a informação de data de último serviço dos serviços SEIT hospedados no Interlegis.')

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])
        queryset = Servico.objects.exclude(url="").exclude(tipo_servico__string_pesquisa="")
        for obj in queryset:
            obj.atualiza_data_uso()
            if ((verbosity == 1) and (obj.data_ultimo_uso is None)) or (verbosity > 1):
                self.stdout.write(u"%s \t %s \t %s\n" % (obj.url, obj.data_ultimo_uso, obj.erro_atualizacao))
