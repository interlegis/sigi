#!/usr/bin/env python
# coding: utf-8

"""
Script para fazer a migração dos dados do SIGI antigo (Access), exportados para
CSV, para o novo SIGI.

Conversão dos dados para CSV::

  mdb-export -d "|" -D "%Y-%m-%d" <database>.mdb "Assembléias" > assembleias.csv
  mdb-export -d "|" -D "%Y-%m-%d" <database>.mdb "municipios" > casas.csv
  mdb-export -d "|" -D "%Y-%m-%d" <database>.mdb "municipios_equipamentos" > equipamentos.csv

Coloque os arquivos no diretório deste script e execute ``./migra.py`` para
fazer a migração.

Nota: é recomendado que o banco de dados esteja em seu estado inicial (de
pós-instalação) para a migração dos dados. Este script não foi feito para um
banco de dados em produção.
"""

from django.core.management import setup_environ
from sigi import settings
setup_environ(settings)

import csv
from sigi.apps.casas.models import *
from sigi.apps.contatos.models import *
from sigi.apps.convenios.models import *
from sigi.apps.inventario.models import *
from sigi.apps.mesas.models import *
from sigi.apps.parlamentares.models import *

ERROR_MSG_0 = ('<ERRO> %s[%s]: erro desconhecido! Possível erro de integridade '
               'do banco de dados. Favor verificar e inserir manualmente caso '
               'necessário.')
ERROR_MSG_1 = ('<ERRO> %s[%s]: erro ao inserir item, será necessário inserção '
               'manual.')

def migra_assembleias(filename):
    """ TODO: CNPJ """
    # identificação das colunas nos arquivo CSV
    UF_COL = 5
    NOME_COL = 8
    ENDERECO_COL = 39
    CEP_COL = 40
    EMAIL_COL = 41
    PAGINA_COL = 43
    OBS_COL = 37
    FONE_1_COL = 32
    FONE_2_COL = 33
    FAX_COL = 34
    FONE_PREFEITURA = 35
    PRESIDENTE_COL = 38
    EMAIL_PRESIDENTE_COL = 42
    REPRESENTANTE_COL = 83

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()

    for line in reader:
        municipio = Municipio.objects.get(uf__sigla=line[UF_COL], is_capital=True)
        casa = CasaLegislativa(
            municipio=municipio,
            nome=line[NOME_COL],
            tipo='AL',
            logradouro=line[ENDERECO_COL],
            cep=line[CEP_COL],
            email=line[EMAIL_COL],
            pagina_web=line[PAGINA_COL],
            observacoes=line[OBS_COL],
        )
        if line[UF_COL] == 'DF':
            casa.tipo = 'CD'
        casa.save()

        if line[FONE_1_COL]:
            fone1 = Telefone(numero=line[FONE_1_COL], tipo='F', content_object=casa)
            fone1.save()
        if line[FONE_2_COL]:
            fone2 = Telefone(numero=line[FONE_2_COL], tipo='I', content_object=casa)
            fone2.save()
        if line[FAX_COL]:
            fax = Telefone(numero=line[FAX_COL], tipo='X', content_object=casa)
            fax.save()
        if line[FONE_PREFEITURA]:
            fone_prefeitura = Telefone(
                numero=line[FONE_PREFEITURA],
                tipo='F',
                content_object=casa,
                nota='Telefone da Prefeitura.'
            )
            fone_prefeitura.save()

        if line[REPRESENTANTE_COL]:
            representante = Contato(nome=line[REPRESENTANTE_COL], content_object=casa)
            representante.save()

        if line[PRESIDENTE_COL]:
            mesa = MesaDiretora(casa_legislativa=casa)
            mesa.save()
            parlamentar = Parlamentar(nome_completo=line[PRESIDENTE_COL], email=line[EMAIL_PRESIDENTE_COL])
            parlamentar.save()
            cargo_presidente = Cargo.objects.get(descricao__iexact='presidente')
            presidente = MembroMesaDiretora(
                parlamentar=parlamentar,
                cargo=cargo_presidente,
                mesa_diretora=mesa
                )
            presidente.save()


def migra_casas(filename):
    """ TODO: CNPJ """
    # identificação das colunas no arquivo CSV
    COD_IBGE_COL = 1
    NOME_COL = 8
    ENDERECO_COL = 39
    CEP_COL = 40
    EMAIL_COL = 41
    PAGINA_COL = 43
    OBS_COL = 37
    FONE_1_COL = 32
    FONE_2_COL = 33
    FAX_COL = 34
    FONE_PREFEITURA = 35
    PRESIDENTE_COL = 38
    EMAIL_PRESIDENTE_COL = 42
    REPRESENTANTE_COL = 83

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1
    for line in reader:
        linenum += 1

        try:
            municipio = Municipio.objects.get(codigo_ibge=line[COD_IBGE_COL])
        except Municipio.DoesNotExist:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except ValueError:
            print ERROR_MSG_1 % (filename, linenum)
            continue

        casa = CasaLegislativa(
            municipio=municipio,
            nome=line[NOME_COL],
            tipo='CM',
            logradouro=line[ENDERECO_COL],
            cep=line[CEP_COL],
            email=line[EMAIL_COL],
            pagina_web=line[PAGINA_COL],
            observacoes=line[OBS_COL],
        )
        try:
            casa.save()
        except:
            print ERROR_MSG_0 % (filename, linenum)
            continue

        if line[FONE_1_COL]:
            fone1 = Telefone(numero=line[FONE_1_COL], tipo='F', content_object=casa)
            fone1.save()
        if line[FONE_2_COL]:
            fone2 = Telefone(numero=line[FONE_2_COL], tipo='I', content_object=casa)
            fone2.save()
        if line[FAX_COL]:
            fax = Telefone(numero=line[FAX_COL], tipo='X', content_object=casa)
            fax.save()
        if line[FONE_PREFEITURA]:
            fone_prefeitura = Telefone(
                numero=line[FONE_PREFEITURA],
                tipo='F',
                content_object=casa,
                nota='Telefone da Prefeitura.'
            )
            fone_prefeitura.save()

        if line[REPRESENTANTE_COL]:
            representante = Contato(nome=line[REPRESENTANTE_COL], content_object=casa)
            representante.save()

        if line[PRESIDENTE_COL]:
            mesa = MesaDiretora(casa_legislativa=casa)
            mesa.save()
            parlamentar = Parlamentar(nome_completo=line[PRESIDENTE_COL], email=line[EMAIL_PRESIDENTE_COL])
            parlamentar.save()
            cargo_presidente = Cargo.objects.get(descricao__iexact='presidente')
            presidente = MembroMesaDiretora(
                parlamentar=parlamentar,
                cargo=cargo_presidente,
                mesa_diretora=mesa
            )
            presidente.save()

def migra_equipamentos(filename):
    UF_COL = 3
    NOME_CASA_COL = 4
    N_IMPRESSORA_COL = 51
    N_NOVADATA_COL = 48
    N_MICROCOMP_COL = 47
    N_MONITOR_COL = 52
    N_MODEM_COL = 53
    N_WEBCAM_COL = 55
    N_ROUTER_COL = 54
    N_ESTABILIZADOR = 56
    QUEM_RECEBEU_COL = 57

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1

    for line in reader:
        linenum += 1
        try:
            casa = CasaLegislativa.objects.get(nome=line[NOME_CASA_COL]])
        except CasaLegislativa.DoesNotExist:
            print ERROR_MSG_1 % (filename, linenum)
            continue

        fornecedor = Fornecedor.objects.get(nome__iexact="desconhecido")

        if line[N_IMPRESSORA_COL]:
            impressora = Equipamento.objects.get(id=2)
            bem = Bem(
                casa_legislativa=casa,
                fornecedor=fornecedor,
                equipamento=impressora,
                recebido_por=line[QUEM_RECEBEU_COL]
            )
            bem.save()

        if line[N_NOVADATA_COL]:
            novadata = Equipamento.objects.get(id=1)
            bem = Bem(
                casa_legislativa=casa,
                fornecedor=fornecedor,
                equipamento=novadata,
                recebido_por=line[QUEM_RECEBEU_COL],
                observacoes=('Número de nota de equipamento NOVADATA importado ',
                             'do SIGI antigo.')
            )
            bem.save()

        if line[N_MICROCOMP_COL]:
            microcomp = Equipamento.objects.get(id=3)
            bem = Bem(
                casa_legislativa=casa,
                fornecedor=fornecedor,
                equipamento=microcomp,
                recebido_por=line[QUEM_RECEBEU_COL]
            )
            bem.save()

        if line[N_MONITOR_COL]:
            monitor = Equipamento.objects.get(id=6)
            bem = Bem(
                casa_legislativa=casa,
                fornecedor=fornecedor,
                equipamento=monitor,
                recebido_por=line[QUEM_RECEBEU_COL]
            )
            bem.save()

        if line[N_MODEM_COL]:
            modem = Equipamento.objects.get(id=5)
            bem = Bem(
                casa_legislativa=casa,
                fornecedor=fornecedor,
                equipamento=modem,
                recebido_por=line[QUEM_RECEBEU_COL]
            )
            bem.save()

        if line[N_WEBCAM_COL]:
            webcam = Equipamento.objects.get(id=9)
            bem = Bem(
                casa_legislativa=casa,
                fornecedor=fornecedor,
                equipamento=webcam,
                recebido_por=line[QUEM_RECEBEU_COL]
            )
            bem.save()

        if line[N_ROUTER_COL]:
            roteador = Equipamento.objects.get(id=8)
            bem = Bem(
                casa_legislativa=casa,
                fornecedor=fornecedor,
                equipamento=roteador,
                recebido_por=line[QUEM_RECEBEU_COL]
            )
            bem.save()

        if line[N_ESTABILIZADOR]:
            estabilizador = Equipamento.objects.get(id=4)
            bem = Bem(
                casa_legislativa=casa,
                fornecedor=fornecedor,
                equipamento=estabilizador,
                recebido_por=line[QUEM_RECEBEU_COL]
            )
            bem.save()

def migra_convenios(filename):
    # identificação das colunas no arquivo CSV
    STATUS_COL = 8
    NUM_PROCESSO_SF_COL = 39
    DATA_ADESAO_COL = 1
    DATA_TERMO_ACEITE_COL = 40
    DATA_RETORNO_ASSINATURA = 43
    DATA_PUB_DIARIO = 37
    DATA_DEV_VIA_CONV_CM = 32
    DATA_POSTAGEM_CORREIO = 33
    RECEBEU_ESTACAO = 34
    RECEBIDOS_COMO_PREVISTO = 35

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1
    for line in reader:
        linenum += 1


if __name__ == '__main__':
    print "<iniciando migração de equipamentos>"
    migra_equipamentos('equipamentos.csv')
    print "<iniciando migração das assembléias legislativas>"
    migra_assembleias('assembleias.csv')
    print "<iniciando migração das demais casas legislativas>"
    migra_casas('casas.csv')
    print "<iniciando migração dos convênios>"
    # migra_convenios('casas.csv')
