# -*- coding: utf-8 -*-

import csv
import os
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from sigi.apps.utils import to_ascii
from sigi.apps.servicos.models import Servico, TipoServico
from sigi.apps.casas.models import Orgao, Funcionario

class Command(BaseCommand):
    args = "nome_do_arquivo.txt"
    help = u"""
Importa dados de serviços de arquivos TXT gerados pela COTIN.
"""
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError(u"Informe UM arquivo TXT a importar")
        file_name = args[0]

        self.stdout.write(u'Verificando estrutura do arquivo...')
        if not os.path.isfile(file_name):
            raise CommandError(u"Arquivo '%s' não encontrado" % file_name)

        with open(file_name, 'r') as f:
            reader = csv.DictReader(f, delimiter=" ")
            if (not 'TEMPLATE' in reader.fieldnames or
                not 'NAME' in reader.fieldnames or
                not 'COD_ORGAO' in reader.fieldnames):
                raise CommandError(u"Formato inválido do arquivo.")
            self.stdout.write(u'Estrutura parece ok.')
            self.stdout.write("Preparando dados...")
            casas = {
                to_ascii(c.municipio.nome).replace(' ','').replace('-','').lower()
                + '-' + to_ascii(c.municipio.uf.sigla).lower(): c.pk
                for c in Orgao.objects.filter(tipo__sigla='CM')
            }
            casas.update(
                {'al-'+to_ascii(c.municipio.uf.sigla).lower(): c.pk
                for c in Orgao.objects.filter(tipo__sigla='AL')}
            )
            casas.update(
                {'tce-'+to_ascii(c.municipio.uf.sigla).lower(): c.pk
                for c in Orgao.objects.filter(tipo__sigla='TCE')}
            )
            self.stdout.write("Processando...")

            lista_tipos = set()
            agora = datetime.now()
            subdominios = {'PM': 'www', 'SAPL': 'sapl',
                           'EmailLeg': 'correioadm', 'edem': 'edemocracia',
                           'LEGBR': '', 'GOVBR': ''}
            can_deactivate = True

            for rec in reader:
                nome = rec['NAME']
                sigla = rec['TEMPLATE']
                cod_orgao = rec['COD_ORGAO']

                if sigla == 'DNS':
                    dominio = nome
                    if '.leg.br' in nome:
                        nome = nome.replace('.leg.br', '')
                        sigla = 'LEGBR'
                    elif '.gov.br' in nome:
                        nome = nome.replace('.gov.br', '')
                        if nome.startswith('camara'):
                            nome = nome.replace('camara', '')
                        if nome.startswith('cm'):
                            nome = nome.replace('cm','')
                        sigla = 'GOVBR'
                    nome = nome.replace('.', '-')
                else:
                    dominio = nome.replace('-','.')+'.leg.br'

                url = u"https://{subdominio}.{dominio}".format(
                    subdominio=subdominios[sigla],
                    dominio=dominio
                )
                tipo_servico = TipoServico.objects.get(sigla=sigla)
                lista_tipos.add(tipo_servico)

                if cod_orgao is not None:
                    if cod_orgao == '*':
                        self.stdout.write(
                            "{template} {name} {cod_orgao} "
                            "registro ignorado".format(
                                template=rec['TEMPLATE'],
                                name=rec['NAME'],
                                cod_orgao=rec['COD_ORGAO']
                            )
                        )
                        continue
                    else:
                        casa = Orgao.objects.get(id=cod_orgao)
                else:
                    if nome not in casas:
                        self.stdout.write(
                            "{template} {name} {cod_orgao} "
                            "orgao nao encontrado ({s})".format(
                                template=rec['TEMPLATE'],
                                name=rec['NAME'],
                                cod_orgao=rec['COD_ORGAO'],
                                s=nome
                            )
                        )
                        can_deactivate = False
                        continue
                    casa = Orgao.objects.get(id=casas[nome])

                try:
                    contato, created = casa.funcionario_set.get_or_create(
                        setor='contato_interlegis',
                        defaults={'nome': u"<<CRIADO PELO SISTEMA>>"}
                    )
                except Funcionario.MultipleObjectsReturned:
                    contato = casa.funcionario_set.filter(
                        setor='contato_interlegis',
                    ).first() # Hack - pega sempre o primeiro

                try:
                    servico, created = casa.servico_set.get_or_create(
                        tipo_servico=tipo_servico,
                        data_desativacao=None,
                        defaults={
                            'contato_tecnico': contato,
                            'contato_administrativo': contato,
                            'url': url,
                            'hospedagem_interlegis': True,
                            'data_ativacao': date.today()
                        }
                    )
                    servico.save()
                except Servico.MultipleObjectsReturned:
                    self.stdout.write(
                        u"{template} {name} mais de um servico encontrado "
                        u"({s})".format(template=rec['TEMPLATE'],
                                        name=rec['NAME'], s=nome)
                    )
                    can_deactivate = False


            if can_deactivate:
                for tipo_servico in lista_tipos:
                    tipo_servico.servico_set.filter(
                        data_alteracao__lt=agora
                    ).update(
                        data_desativacao=agora,
                        motivo_desativacao=(u"[AUTOMÁTICO] Não consta da lista "
                                            u"da COTIN")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(u"Os serviços excendentes não podem ser "
                                     u"desativados porque foram encontradas "
                                     u"inconsistências no arquivo de origem")
                )


