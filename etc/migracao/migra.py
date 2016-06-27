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

import csv
from datetime import datetime

from django.core.management import setup_environ

from sigi import settings
from sigi.apps.casas.models import *
from sigi.apps.contatos.models import *
from sigi.apps.convenios.models import *
from sigi.apps.inventario.models import *
from sigi.apps.parlamentares.models import *

setup_environ(settings)


ERROR_MSG_0 = ('<ERRO> %s[%s]: erro desconhecido! Possível erro de integridade '
               'do banco de dados. Favor verificar e inserir manualmente caso '
               'necessário.')
ERROR_MSG_1 = ('<ERRO> %s[%s]: erro ao inserir item, será necessário inserção '
               'manual.')
OBS_CONVENIO = ('Convênio sem termo de adesão')


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

    tipo_casa = TipoCasaLegislativa.objects.filter(sigla='AL').get()

    for line in reader:
        uf = UnidadeFederativa.objects.get(sigla=line[UF_COL])
        municipio = Municipio.objects.get(uf=uf, is_capital=True)
        aux_end = line[ENDERECO_COL].split('-')
        bairro = ''
        if(aux_end.__len__() > 1):
            bairro = aux_end[1].replace(' ', '', 1)
        else:
            bairro = ''
        casa = CasaLegislativa(
            municipio=municipio,
            nome=line[NOME_COL],
            tipo=tipo_casa,
            logradouro=aux_end[0],
            bairro=bairro,
            cep=line[CEP_COL],
            email=line[EMAIL_COL],
            pagina_web=line[PAGINA_COL],
            observacoes=line[OBS_COL],
            presidente=line[PRESIDENTE_COL],
            telefone=line[FONE_1_COL]
        )
        if line[UF_COL] == 'DF':
            casa.tipo = TipoCasaLegislativa.objects.filter(sigla='CT').get()
        casa.save()

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
# Presidente será um atributo de casa legislativa
#        if line[REPRESENTANTE_COL]:
#            representante = Contato(nome=line[REPRESENTANTE_COL], content_object=casa)
#            representante.save()

#        if line[PRESIDENTE_COL]:
#            mesa = MesaDiretora(casa_legislativa=casa)
#            mesa.save()
#            parlamentar = Parlamentar(nome_completo=line[PRESIDENTE_COL], email=line[EMAIL_PRESIDENTE_COL])
#            parlamentar.save()
#            cargo_presidente = Cargo.objects.get(descricao__iexact='presidente')
#            presidente = MembroMesaDiretora(
#                parlamentar=parlamentar,
#                cargo=cargo_presidente,
#                mesa_diretora=mesa
#                )
#            presidente.save()


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
    tipo_casa = TipoCasaLegislativa.objects.filter(sigla='CM').get()

    linenum = 1
    for line in reader:
        linenum += 1
        try:
            municipio = Municipio.objects.get(codigo_ibge=line[COD_IBGE_COL])
        except Municipio.DoesNotExist:
            print "Municipio não existe"
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except ValueError:
            print ERROR_MSG_1 % (filename, linenum)
            continue

        aux_end = line[ENDERECO_COL].split('-')
        bairro = ''
        if(aux_end.__len__() > 1):
            bairro = aux_end[1].replace(' ', '', 1)
        casa = CasaLegislativa(
            municipio=municipio,
            nome='Câmara Municipal de ' + line[NOME_COL],
            tipo=tipo_casa,
            logradouro=aux_end[0],
            bairro=bairro,
            cep=line[CEP_COL],
            email=line[EMAIL_COL],
            pagina_web=line[PAGINA_COL],
            observacoes=line[OBS_COL],
            presidente=line[PRESIDENTE_COL],
            telefone=line[FONE_1_COL]
        )

        try:
            casa.save()
        except:
            print "Erro ao inserir casa..."
            print ERROR_MSG_0 % (filename, linenum)
            continue

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
    # DATA_DEV_VIA_CONV_CM_100 = 32 Não foi registrado para as 100
    #DATA_POSTAGEM_CORREIO_100 = 26

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1
    ###Geração de arquivos para análise###
    import codecs
    f1 = codecs.open('file1.txt', 'w', encoding="utf-8")
    f1.write(u'Casas que não tem Número Processo Senado Federal\n')
    f2 = codecs.open('file2.txt', 'w', encoding="utf-8")
    f2.write(u'Casas que não tem data de adesão e não tem convênio mas recebeu equipamentos\n')
    ######
    for line in reader:
        linenum += 1

        try:
            casa = CasaLegislativa.objects.get(municipio__codigo_ibge=line[COD_IBGE_COL])
        except CasaLegislativa.DoesNotExist:
            print "Erro ao inserir convênio. Casa não existe"
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except CasaLegislativa.MultipleObjectsReturned:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except ValueError:
            print ERROR_MSG_1 % (filename, linenum)
            continue

        # Se o convênio não tiver data de adesão mas tiver data retorno assinatura copiar essa data para a data de adesão.
        obs = ''
        projeto = None
        convenio1 = None
        convenio2 = None
        if line[DATA_ADESAO_COL] == '1001-01-01' and line[DATA_RETORNO_ASSINATURA].__len__() != 0:
            line[DATA_ADESAO_COL] = line[DATA_RETORNO_ASSINATURA]
            obs = OBS_CONVENIO

        if line[DATA_ADESAO_COL] != '1001-01-01':
            projeto = Projeto.objects.get(id=1)

        if projeto:
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
                observacao=obs,)

        ###Relatório###
        if((projeto or line[DATA_TERMO_ACEITE_COL]) and line[NUM_PROCESSO_SF_COL].__len__() == 0):
            f1.write(casa.nome + "," + casa.municipio.uf.sigla + "\n")
        if(projeto is None and line[DATA_TERMO_ACEITE_COL].__len__() != 0):
            f2.write(casa.nome + "," + casa.municipio.uf.sigla + "\n")
        ######
        projeto = None
        obs = ''
        if line[DATA_ADESAO_100_COL] == '1001-01-01' and line[DATA_RETORNO_ASSINATURA_100_COL].__len__() != 0:
            line[DATA_ADESAO_100_COL] = line[DATA_RETORNO_ASSINATURA_100_COL]
            obs = OBS_CONVENIO
        if line[DATA_ADESAO_100_COL] != '1001-01-01':
            projeto = Projeto.objects.get(id=2)

        if projeto:
            convenio2 = Convenio(
                casa_legislativa=casa,
                projeto=projeto,
                num_processo_sf=line[NUM_PROCESSO_SF_100_COL],
                num_convenio=line[NUM_CONVENIO_100_COL],
                data_adesao=get_datetime_obj(line[DATA_ADESAO_100_COL]),
                data_retorno_assinatura=get_datetime_obj(line[DATA_TERMO_ACEITE_100_COL]),
                data_pub_diario=get_datetime_obj(line[DATA_RETORNO_ASSINATURA_100_COL]),
                data_termo_aceite=get_datetime_obj(line[DATA_PUB_DIARIO_100_COL]),
                observacao=obs,
            )

        try:
            if convenio1:
                convenio1.save()
            if convenio2:
                convenio2.save()
        except:
            print "Erro ao inserir convênio"
            print ERROR_MSG_0 % (filename, linenum)
            continue
    f1.close()
    f2.close()


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
    DATA_PUB_DIARIO = 29

    reader = csv.reader(open(filename, 'r'), delimiter='|', skipinitialspace=True)
    header = reader.next()
    linenum = 1
    tipo_casa = TipoCasaLegislativa.objects.filter(sigla='AL').get()
    for line in reader:
        linenum += 1

        try:
            assembleia = CasaLegislativa.objects.get(municipio__uf__sigla=line[SIGLA_COL], tipo=tipo_casa)
        except CasaLegislativa.DoesNotExist:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except CasaLegislativa.MultipleObjectsReturned:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        except ValueError:
            print ERROR_MSG_1 % (filename, linenum)
            continue
        projeto = Projeto.objects.get(id=2)
        convenio = Convenio(
            casa_legislativa=assembleia,
            num_processo_sf=line[NUM_PROCESSO_SF_COL],
            num_convenio=line[NUM_CONVENIO_COL],
            projeto=projeto,
            data_adesao=get_datetime_obj(line[DATA_ADESAO_COL]),
            data_retorno_assinatura=get_datetime_obj(line[DATA_TERMO_ACEITE_COL]),
            data_pub_diario=get_datetime_obj(line[DATA_RETORNO_ASSINATURA]),
            data_termo_aceite=get_datetime_obj(line[DATA_PUB_DIARIO]),
        )
        try:
            convenio.save()
        except:
            print ERROR_MSG_0 % (filename, linenum)
            print convenio
            continue


def popula():
    """
        Será preciso cadastrar no banco os seguintes Projeto:
        1 - Projeto Interlegis
        2 - Projeto Piloto de Modernização
        3 - Projeto Modernização Legislativo
    """

    projeto1 = Projeto(sigla='PI', nome='Projeto Interlegis')
    projeto1.save()
    projeto2 = Projeto(sigla='PPM', nome='Projeto Piloto de Modernização')
    projeto2.save()
    projeto3 = Projeto(sigla='PML', nome='Projeto Modernização Legislativo')
    projeto3.save()

    tipo1 = TipoCasaLegislativa(sigla='CM', nome='Câmara Municipal')
    tipo1.save()
    tipo2 = TipoCasaLegislativa(sigla='AL', nome='Assembléia Legislativa')
    tipo2.save()
    tipo3 = TipoCasaLegislativa(sigla='CT', nome='Câmara Distrital')
    tipo3.save()


if __name__ == '__main__':
    popula()
    print "<iniciando migração das assembléias legislativas>"
    migra_assembleias('assembleias.csv')
    print "<iniciando migração das demais casas legislativas>"
    migra_casas('casas.csv')
    print "<iniciando migração dos CNPJ das casas>"
    migra_cnpj('cnpj.csv')
    print "<iniciando migração dos convênios das casas municipais>"
    migra_convenios_casas('casas.csv')
    print "<iniciando migração dos convênios das assembléias>"
    migra_convenios_assembleias('assembleias.csv')
