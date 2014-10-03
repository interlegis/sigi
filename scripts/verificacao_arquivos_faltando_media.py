# -*- coding: utf-8 -*-

# Dependência:
# pip install terminaltables

from terminaltables import AsciiTable

from datetime import datetime
from os.path import isfile

from sigi.apps.convenios.models import Anexo as AnexoConvenios
from sigi.apps.ocorrencias.models import Anexo as AnexoOcorrencias
from sigi.apps.diagnosticos.models import Anexo as AnexoDiagnosticos


novos_faltando = []
antigos_faltando = []
inicio = datetime(2014, 9, 1)

for cl in (AnexoConvenios, AnexoOcorrencias, AnexoDiagnosticos):
    todos = cl.objects.all()
    for a in todos:
        if not isfile(a.arquivo.path):
            nome = a.arquivo.name.split('/')[-1]
            if a.data_pub > inicio:
                # NOVO (só ocorrencias)
                novos_faltando.append([
                    a.ocorrencia.casa_legislativa.municipio.uf.sigla,
                    nome, ])
            else:
                # ANTIGO (só convenios)
                antigos_faltando.append([
                    "https://sigi.interlegis.leg.br/convenios/convenio/%s" % a.convenio.id,
                    a.arquivo.name.split('/')[-1],
                    str(a.data_pub.date())])

novos_faltando = [["UF", "Arquivo"]] + sorted(novos_faltando)
antigos_faltando = [['URL DO CONVENIO', 'NOME DO ARQUIVO', 'DATA']] + sorted(antigos_faltando)


def print_table(msg, relacao):
    print "\n%s:\n" % msg
    table = AsciiTable(relacao)
    print table.table

print_table(u'Anexos de Novas Ocorrências faltando (desde %s)' % inicio, novos_faltando)
print_table(u'Anexos de Convênios Antigos faltando (até %s)' % inicio, antigos_faltando)
