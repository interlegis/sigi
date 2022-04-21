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
    help = """
Importa dados de serviços de arquivos TXT gerados pela COTIN.
"""
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Informe UM arquivo TXT a importar")
        file_name = args[0]

        self.stdout.write('Verificando estrutura do arquivo...')
        if not os.path.isfile(file_name):
            raise CommandError("Arquivo '%s' não encontrado" % file_name)

        with open(file_name, 'r') as f:
            reader = csv.DictReader(f, delimiter=" ")
            if (not 'TEMPLATE' in reader.fieldnames or
                not 'NAME' in reader.fieldnames or
                not 'COD_ORGAO' in reader.fieldnames):
                print (reader.fieldnames)
                raise CommandError("Formato inválido do arquivo.")
            self.stdout.write('Estrutura parece ok.')
            self.stdout.write("Preparando dados...")
            casas = {
                to_ascii(c.municipio.nome).replace(' ','').replace('-','').replace("'", '').lower()
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
                name = rec['NAME']
                template = rec['TEMPLATE']
                cod_orgao = rec['COD_ORGAO']

                if template == 'DNS':
                    s = name.split('.')
                    nome_casa = s[0]+"-"+s[1]
                    dominio = s[0]
                    sufixo = ".".join(s[1:])
                    if '.leg.br' in name:
                        sigla = 'LEGBR'
                    elif '.gov.br' in name:
                        sigla = 'GOVBR'
                else:
                    s = name.split("-")
                    nome_casa = name
                    dominio = name[0]
                    sufixo = ".".join(s[1:]) + '.leg.br'
                    sigla = template

                if nome_casa.startswith('camara'):
                    nome_casa = nome_casa.replace('camara', '')
                if nome_casa.startswith('cm'):
                    nome_casa = nome_casa.replace('cm','')

                url = "https://{subdominio}.{dominio}.{sufixo}".format(
                    subdominio=subdominios[sigla],
                    dominio=dominio,
                    sufixo=sufixo
                )
                tipo_servico = TipoServico.objects.get(sigla=sigla)
                lista_tipos.add(tipo_servico)

                if cod_orgao is not None:
                    if cod_orgao == '*':
                        self.stdout.write(
                            "{template} {name} {cod_orgao} "
                            "registro ignorado".format(
                                template=template,
                                name=name,
                                cod_orgao=cod_orgao
                            )
                        )
                        continue
                    else:
                        try:
                            casa = Orgao.objects.get(id=cod_orgao)
                        except Orgao.DoesNotExist:
                            self.stdout.write(
                                "{template} {name} {cod_orgao} "
                                "codigo inexistente".format(
                                    template=template,
                                    name=name,
                                    cod_orgao=cod_orgao
                                )
                            )
                            can_deactivate = False
                            continue
                else:
                    if nome_casa in casas:
                        casa = Orgao.objects.get(id=casas[nome_casa])
                    else:
                        # Nome pode divergir, vamos procurar pelo domínio
                        try:
                            servico = Servico.objects.get(
                                url__icontains=dominio,
                                tipo_servico=tipo_servico
                            )
                            servico.save()
                            continue
                        except (Servico.DoesNotExist,
                                Servico.MultipleObjectsReturned):
                            # tenta descobrir outro serviço do mesmo domínio
                            casa = None
                            for servico in Servico.objects.filter(
                                url__icontains=dominio):
                                if casa is None:
                                    casa = servico.casa_legislativa
                                elif casa != servico.casa_legislativa:
                                    # Mais de uma casa usando o mesmo domínio!!!
                                    casa = None
                                    break
                        if casa is None: # Impossível identificar a casa
                            self.stdout.write(
                                "{template} {name} {cod_orgao} "
                                "orgao nao encontrado ({s})".format(
                                    template=template,
                                    name=name,
                                    cod_orgao=cod_orgao,
                                    s=nome_casa
                                )
                            )
                            can_deactivate = False
                            continue

                try:
                    contato, created = casa.funcionario_set.get_or_create(
                        setor='contato_interlegis',
                        defaults={'nome': "<<CRIADO PELA IMPORTAÇÃO DE SERVIÇOS SEIT>>"}
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
                        "{template} {name} {cod_orgao} mais de um servico "
                        "encontrado ({s})".format(
                            template=template,
                            name=name,
                            cod_orgao=cod_orgao,
                            s=nome_casa
                        )
                    )
                    can_deactivate = False

            if can_deactivate:
                for tipo_servico in lista_tipos:
                    tipo_servico.servico_set.filter(
                        data_alteracao__lt=agora
                    ).update(
                        data_desativacao=agora,
                        motivo_desativacao=("[AUTOMÁTICO] Não consta da lista "
                                            "da COTIN")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR("Os serviços excendentes não podem ser "
                                     "desativados porque foram encontradas "
                                     "inconsistências no arquivo de origem")
                )


