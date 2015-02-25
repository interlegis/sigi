# -*- coding: utf-8 -*-
from dados_gerentes import atrib, gerentes
from sigi.apps.casas.models import CasaLegislativa


def salvar():
    for cod, abrev_gerente in atrib:
        casas = CasaLegislativa.objects.filter(municipio__codigo_ibge=cod, tipo__sigla='CM')
        if not casas:
            print '############################# SEM CASA: ', cod
        elif len(casas) > 1:
            print '############################# VÁRIAS CASAS: ', cod, casas
        else:
            [c] = casas
            c.gerente_contas = gerentes[abrev_gerente]
            c.save()
