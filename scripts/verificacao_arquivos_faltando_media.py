# -*- coding: utf-8 -*-

# Dependência:
# pip install terminaltables
from os.path import isfile

from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from terminaltables import AsciiTable

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.convenios.models import Anexo as AnexoConvenios
from sigi.apps.diagnosticos.models import Anexo as AnexoDiagnosticos
from sigi.apps.ocorrencias.models import Anexo as AnexoOcorrencias
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.servidores.models import Servidor


def print_table(msg, relacao):
    print "\n%s:\n" % msg
    table = AsciiTable(relacao)
    print table.table


# IMAGENS FALTANDO
imagens_faltando = [[u"SITUAÇÃO DO ARQUIVO DA FOTO  ", "URL", "OBJETO"]]
for cl in (CasaLegislativa, Parlamentar, Servidor):
    content_type = ContentType.objects.get_for_model(cl)
    url_base = "admin:%s_%s_change" % (content_type.app_label, content_type.model)
    for a in cl.objects.all():
        if a.foto:
            url = reverse(url_base, args=(a.pk,))
            imagens_faltando.append([
                "PRESENTE" if isfile(a.foto.path) else "FALTANDO",
                url,
                unicode(a)])

print_table(u"Relação de todas as fotos de Casas Legislativas, Parlamentares e Servidores", imagens_faltando)


novos_faltando = []
antigos_faltando = []
inicio = datetime(2014, 9, 1)

for cl in (AnexoConvenios, AnexoOcorrencias, AnexoDiagnosticos):
    for a in cl.objects.all():
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

print_table(u'Anexos de Novas Ocorrências faltando (desde %s)' % inicio, novos_faltando)
print_table(u'Anexos de Convênios Antigos faltando (até %s)' % inicio, antigos_faltando)
