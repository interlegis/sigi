#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para fazer a migração dos dados do SIGI antigo (Access), exportados para
CSV, para o novo SIGI.

Conversão dos dados para CSV::

  mdb-export -d "|" -D "%Y-%m-%d" <database>.mdb "Assembléias" > assembleias.csv
  mdb-export -d "|" -D "%Y-%m-%d" <database>.mdb "municipios" > casas.csv
  mdb-export -d "|" -D "%Y-%m-%d" <database>.mdb "CNPJ DAS CM" > cnpj.csv

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
from datetime import datetime
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
    # identificação das colunas nos arquivo CSV
    UF_COL = 5
    NOME_COL = 8
    FONE_1_COL = 32
    FONE_2_COL = 33
    FAX_COL = 34
    FONE_PREFEITURA = 35
    OBS_COL = 37
    PRESIDENTE_COL = 38
    ENDERECO_COL = 39
    CEP_COL = 40
    EMAIL_COL = 41
    EMAIL_PRESIDENTE_COL = 42
    PAGINA_COL = 43
    #REPRESENTANTE_COL = 86

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()

    for line in reader:
        UF = UnidadeFederativa.objects.get(sigla=line[UF_COL])
        municipio = Municipio.objects.get(municipio__codigo_ibge=line[UF_COL], is_capital=True)
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
            casa.tipo = 'CT'
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

#        if line[REPRESENTANTE_COL]:
#            representante = Contato(nome=line[REPRESENTANTE_COL], content_object=casa)
#            representante.save()

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
    # identificação das colunas no arquivo CSV
    COD_IBGE_COL = 1
    COD_TSE_COL = 2
    NOME_COL = 8
    ENDERECO_COL = 40
    CEP_COL = 41
    EMAIL_COL = 42
    PAGINA_COL = 44
    OBS_COL = 38
    FONE_1_COL = 33
    FONE_2_COL = 34
    FAX_COL = 35
    FONE_PREFEITURA = 36
    PRESIDENTE_COL = 39
    EMAIL_PRESIDENTE_COL = 43
    REPRESENTANTE_COL = 85

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1
    for line in reader:
        linenum += 1
        try:
            municipio = Municipio.objects.get(codigo_ibge=line[COD_IBGE_COL])
            #print line[COD_IBGE_COL]
            #var =  raw_input()
            print municipio.codigo_ibge
        except Municipio.DoesNotExist:
            print "Municipio não existe"
            #var =  raw_input()
            #print line[COD_IBDE_COL]
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except ValueError:
            var =  raw_input()
            print ERROR_MSG_1 % (filename, linenum)
            continue
        casa = CasaLegislativa(
            municipio=municipio,
            nome='Câmara Municipal de ' + line[NOME_COL],
            tipo='CM',
            logradouro=line[ENDERECO_COL],
            cep=line[CEP_COL],
            email=line[EMAIL_COL],
            pagina_web=line[PAGINA_COL],
            observacoes=line[OBS_COL],
        )
        #print casa.nome
        try:
            casa.save()
        except:
            print "Erro ao inserir casa"
            #var =  raw_input("teste")
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

def migra_cnpj(filename):
    # identificação das colunas no arquivo CSV
    COD_TSE_COL = 0
    COD_CNPJ1_COL = 3
    COD_CNPJ2_COL = 4

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1
    for line in reader:
        linenum += 1

        try:
            casa = CasaLegislativa.objects.get(municipio__codigo_tse=line[COD_TSE_COL])
        except CasaLegislativa.DoesNotExist:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except CasaLegislativa.MultipleObjectsReturned:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except ValueError:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        casa.cnpj = line[COD_CNPJ1_COL] if not 'EM BRANCO' in line[COD_CNPJ1_COL] else line[COD_CNPJ2_COL]
        casa.save()

def migra_convenios_casas(filename):
    """
        Será preciso cadastrar no banco os seguintes Projeto:
        1 - Sem Projeto
        2 - Projeto Interlegis
        3 - Programa Piloto de Modernização
    """
    def get_datetime_obj(data):
        ldata = data.split('-')
        if len(ldata) != 3:
            return None
        return datetime(int(ldata[0]), int(ldata[1]), int(ldata[2]))

    # identificação das colunas no arquivo CSV
    # No arquivo CSV colunas que contém _100 são do Programa Interlegis
    COD_IBGE_COL = 1

    DATA_ADESAO_COL = 10
    DATA_TERMO_ACEITE_COL = 21
    NUM_CONVENIO_COL = 23
    DATA_POSTAGEM_CORREIO = 26
    NUM_PROCESSO_SF_COL = 27
    DATA_RETORNO_ASSINATURA = 28
    DATA_PUB_DIARIO = 30
    DATA_DEV_VIA_CONV_CM = 32

    DATA_ADESAO_100_COL = 11
    DATA_TERMO_ACEITE_100_COL = 22
    NUM_CONVENIO_100_COL = 24
    NUM_PROCESSO_SF_100_COL = 25
    DATA_RETORNO_ASSINATURA_100_COL = 29
    DATA_PUB_DIARIO_100_COL = 31
    #DATA_DEV_VIA_CONV_CM_100 = 32 Não foi registrado para as 100
    #DATA_POSTAGEM_CORREIO_100 = 26

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1
    for line in reader:
        linenum += 1

        try:
            casa = CasaLegislativa.objects.get(municipio__codigo_ibge=line[COD_IBGE_COL])
        except CasaLegislativa.DoesNotExist:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except CasaLegislativa.MultipleObjectsReturned:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except ValueError:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        if line[DATA_ADESAO_COL]=='1001-01-01':#Sem Projeto
            line[DATA_ADESAO_COL]=''
            projeto = Projeto.objects.get(id=1)
        else:
            projeto = Projeto.objects.get(id=2)

        if(projeto.id!=1 or line[NUM_PROCESSO_SF_COL].__len__()!=0 or 
           line[NUM_CONVENIO_COL].__len__()!=0):
            convenio1 = Convenio(
                casa_legislativa=casa,
                projeto=projeto,
                num_processo_sf=line[NUM_PROCESSO_SF_COL],
                num_convenio=line[NUM_CONVENIO_COL],
                data_adesao=get_datetime_obj(line[DATA_ADESAO_COL]),
                data_retorno_assinatura=get_datetime_obj(line[DATA_TERMO_ACEITE_COL]),
                data_pub_diario=get_datetime_obj(line[DATA_RETORNO_ASSINATURA]),
                data_termo_aceite=get_datetime_obj(line[DATA_PUB_DIARIO]),
                data_devolucao_via=get_datetime_obj(line[DATA_DEV_VIA_CONV_CM]),
                data_postagem_correio=get_datetime_obj(line[DATA_POSTAGEM_CORREIO]),
                )
        if line[DATA_ADESAO_100_COL]=='1001-01-01':#Sem Projeto
            line[DATA_ADESAO_100_COL]=''
            projeto = Projeto.objects.get(id=1)
        else:
            projeto = Projeto.objects.get(id=3)
        if(projeto.id!=1 or line[NUM_PROCESSO_SF_100_COL].__len__()!=0 or
           line[NUM_CONVENIO_100_COL].__len__()!=0):
            convenio2 = Convenio(
            casa_legislativa=casa,
            projeto=projeto,
            num_processo_sf=line[NUM_PROCESSO_SF_100_COL],
            num_convenio=line[NUM_CONVENIO_100_COL],
            data_adesao=get_datetime_obj(line[DATA_ADESAO_100_COL]),
            data_retorno_assinatura=get_datetime_obj(line[DATA_TERMO_ACEITE_100_COL]),
            data_pub_diario=get_datetime_obj(line[DATA_RETORNO_ASSINATURA_100_COL]),
            data_termo_aceite=get_datetime_obj(line[DATA_PUB_DIARIO_100_COL]),
            #            data_devolucao_via=get_datetime_obj(line[DATA_DEV_VIA_CONV_CM]),
            #            data_postagem_correio=get_datetime_obj(line[DATA_POSTAGEM_CORREIO]),
            )

        try:
            if convenio1: convenio1.save()
            if convenio2: convenio2.save()
        except:
            print ERROR_MSG_0 % (filename, linenum)
            continue

def migra_convenios_assembleias(filename):
    def get_datetime_obj(data):
        ldata = data.split('-')
        if len(ldata) != 3:
            return None
        return datetime(int(ldata[0]), int(ldata[1]), int(ldata[2]))

    # identificação das colunas no arquivo CSV
    SIGLA_COL = 5
    DATA_ADESAO_COL = 10
    DATA_TERMO_ACEITE_COL = 21
    NUM_CONVENIO_COL = 23
    NUM_PROCESSO_SF_COL = 26
    DATA_RETORNO_ASSINATURA = 27
    DATA_PUB_DIARIO = 39
    DATA_DEV_VIA_CONV_CM = 31

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1
    for line in reader:
        linenum += 1

        try:
            assembleia = CasaLegislativa.objects.get(municipio__uf__sigla=line[COD_IBGE_COL])
        except CasaLegislativa.DoesNotExist:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except CasaLegistativa.MultipleObjectsReturned:
            print ERROR_MSG_1 % (filename, linenum)
        except ValueError:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        projeto = Projeto.object.get(id=2)
        convenio = Convenio(
            casa_legislativa=assembleia,
            num_processo_sf=line[NUM_PROCESSO_SF_COL],
            num_convenio=line[NUM_CONVENIO_COL],
            projeto=projeto,
            data_adesao=get_datetime_obj(line[DATA_ADESAO_COL]),
            data_retorno_assinatura=get_datetime_obj(line[DATA_TERMO_ACEITE_COL]),
            data_pub_diario=get_datetime_obj(line[DATA_RETORNO_ASSINATURA]),
            data_termo_aceite=get_datetime_obj(line[DATA_PUB_DIARIO]),
            data_devolucao_via=get_datetime_obj(line[DATA_DEV_VIA_CONV_CM]),
            data_postagem_correio=get_datetime_obj(line[DATA_POSTAGEM_CORREIO]),
            )
        try:
            convenio.save()
        except:
            print ERROR_MSG_0 % (filename, linenum)
            continue


if __name__ == '__main__':
#    print "<iniciando migração das assembléias legislativas>"
#    migra_assembleias('assembleias.csv')
#    print "<iniciando migração das demais casas legislativas>"
#    migra_casas('casas.csv')
#    print "<iniciando migração dos CNPJ das casas>"
#    migra_cnpj('cnpj.csv')
    print "<iniciando migração dos convênios das casas municipais>"
    migra_convenios_casas('casas.csv')
#    print "<iniciando migração dos convênios das assembléias>"
#    migra_convenios_assembleias('assembleias.csv')
