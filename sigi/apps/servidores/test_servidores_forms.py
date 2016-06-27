# -*- coding: utf-8 -*-
from datetime import date

import pytest
from django import forms

from sigi.apps.servidores.forms import (Periodo, periodos_se_sobrepoe,
                                        valida_data_inicial_menor_que_final)


@pytest.mark.parametrize('data', [
    dict(ini=1, fim=2),
    pytest.mark.xfail(raises=forms.ValidationError)(dict(ini=2, fim=1)),
    pytest.mark.xfail(raises=forms.ValidationError)(dict(ini=1, fim=1)),
])
def test_valida_data_inicial_menor_que_final(data):
    valida_data_inicial_menor_que_final(data, 'ini', 'fim')


periodos = [
    [Periodo(date(2000, 10, 1), date(2001, 1, 1)), Periodo(date(2001, 1, 1), date(2002, 2, 2)), True],   # um dia de interseção
    [Periodo(date(2000, 10, 1), date(2001, 1, 1)), Periodo(date(2001, 1, 2), date(2002, 2, 2)), False],  # exatamente um dia após
    [Periodo(date(2000, 10, 1), date(2001, 1, 1)), Periodo(date(2000, 12, 2), date(2002, 2, 2)), True],
    [Periodo(date(2000, 10, 1), date(2001, 1, 1)), Periodo(date(2014, 1, 1), date(2014, 2, 2)), False],
]

# para testar que a ordem dos parametros nao importa
periodos_trocados = [[b, a, res] for [a, b, res] in periodos]


@pytest.mark.parametrize('periodo1, periodo2, resultado', periodos + periodos_trocados)
def test_periodos_se_sobrepoe(periodo1, periodo2, resultado):
    assert periodos_se_sobrepoe(periodo1, periodo2) == resultado
