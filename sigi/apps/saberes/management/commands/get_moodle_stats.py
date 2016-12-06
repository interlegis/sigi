# -*- coding: utf-8 -*-
#
# sigi.apps.servicos.management.commands.get_moodle_stats
#
# Copyright (c) 2014 by Interlegis
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
from django.db.models import Avg, Sum
from django.utils.translation import ugettext as _

from sigi.apps.mdl.models import CourseStats, User
from sigi.apps.metas.views import gera_map_data_file
from sigi.apps.saberes.models import CategoriasInteresse, PainelItem


class Command(BaseCommand):
    help = u'Get Moodle data and generate statistical panels.'

    def handle(self, *args, **options):
        areas = []
        numeros = [
            {'descricao': _(u'Total de usuários cadastrados'), 'valor': User.objects.count()},
            {'descricao': _(u'Novos usuários cadastrados'), 'valor': User.objects.filter(firstaccess__gte=1392326052).count()}
        ]

        for ci in CategoriasInteresse.objects.all():
            if ci.coorte:
                total_matriculas = ci.total_alunos_coorte()
            elif ci.apurar_conclusao:
                data = {x['completionstatus']: x for x in CourseStats.objects.filter(category__in=ci.categorias(subcategorias=True)).
                        values('completionstatus').annotate(total_users=Sum('usercount'), grade_average=Avg('gradeaverage'))}
                total_matriculas = sum(x['total_users'] for k, x in data.items())
            else:
                total_matriculas = CourseStats.objects.filter(category__in=ci.categorias(subcategorias=True)). \
                    aggregate(total_users=Sum('usercount'))['total_users']

            dados = [{'descricao': _(u'Total de matrículas'), 'valor': total_matriculas}]

            if ci.coorte:
                for c in ci.categorias(subcategorias=True):
                    dados.append({'descricao': c.name, 'valor': c.total_alunos_cohort()})

            if ci.apurar_conclusao:
                if 'N' in data:
                    dados.append({'descricao': _(u'Matrículas rejeitadas'), 'help_text': _(u'demanda reprimida'),
                                  'valor': data['N']['total_users'], 'percentual': 100.0 * data['N']['total_users'] / total_matriculas})
                    total_alunos = total_matriculas - data['N']['total_users']
                    dados.append({'descricao': _(u'Alunos efetivos'), 'help_text': _(u'os percentuais seguintes se referem a este indicador'),
                                  'valor': total_alunos})
                else:
                    total_alunos = total_matriculas

                if 'C' in data:
                    dados.append({'descricao': _(u'Alunos em curso'), 'valor': data['C']['total_users'],
                                  'percentual': 100.0 * data['C']['total_users'] / total_alunos})
                if 'L' in data:
                    dados.append({'descricao': _(u'Alunos que abandonaram o curso'), 'valor': data['L']['total_users'],
                                  'percentual': 100.0 * data['L']['total_users'] / total_alunos})
                if 'R' in data:
                    dados.append({'descricao': _(u'Alunos reprovados'), 'valor': data['R']['total_users'],
                                  'percentual': 100.0 * data['R']['total_users'] / total_alunos})
                if 'A' in data:
                    dados.append({'descricao': _(u'Alunos aprovados'), 'valor': data['A']['total_users'],
                                  'percentual': 100.0 * data['A']['total_users'] / total_alunos})

                if 'I' in data:
                    dados.append({'descricao': _(u'Situação indefinida'), 'valor': data['I']['total_users'],
                                  'help_text': _(u'Situação do aluno não pode ser determinada pelo sistema'),
                                  'percentual': 100.0 * data['I']['total_users'] / total_alunos})

                if 'A' in data:
                    dados.append({'descricao': _(u'Média das notas dos alunos aprovados (%)'), 'valor': int(data['A']['grade_average'])})

                if 'R' in data:
                    dados.append({'descricao': _(u'Média das notas dos alunos reprovados (%)'), 'valor': int(data['R']['grade_average'])})

            areas.append({'titulo': ci.descricao, 'dados': dados})

        paineis = [{'titulo': _(u'Saberes em números'), 'dados': numeros}] + areas

        PainelItem.objects.all().delete()  # Clear dashboard

        for p in paineis:
            for d in p['dados']:
                PainelItem.objects.create(painel=p['titulo'], descricao=d['descricao'], help_text=d['help_text'] if 'help_text' in
                                          d else '', valor=d['valor'], percentual=d['percentual'] if 'percentual' in d else None)
