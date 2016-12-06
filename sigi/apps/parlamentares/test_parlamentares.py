# -*- coding: utf-8 -*-
import pytest
from django_dynamic_fixture import G

from sigi.apps.parlamentares.models import Parlamentar

pytestmark = pytest.mark.django_db


@pytest.fixture
def some_parliamentarians():
    return parliamentarians_from_names(["Andre Silva", "Bartolomeu Gusmao", "Camila Carla"])


def parliamentarians_from_names(names):
    return [G(Parlamentar, nome_completo=name, foto=None) for name in names]


def test_list_all(some_parliamentarians, app):
    response = app.get('/parlamentares/parlamentar/')
    assert response.status_code == 200

    for x in some_parliamentarians:
        assert x.nome_completo in response.content


def test_list_filtered_by_capital_letter(some_parliamentarians, app):
    response = app.get('/parlamentares/parlamentar/?nome_completo=B')
    assert response.status_code == 200

    a, b, c = some_parliamentarians
    assert a.nome_completo not in response.content
    assert b.nome_completo in response.content
    assert c.nome_completo not in response.content
