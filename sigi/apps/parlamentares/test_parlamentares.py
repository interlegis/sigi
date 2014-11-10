# -*- coding: utf-8 -*-
import pytest
from django_dynamic_fixture import G

from sigi.apps.parlamentares.models import Parlamentar


pytestmark = pytest.mark.django_db


@pytest.fixture
def some_parliamentarians():
    a = G(Parlamentar, nome_completo="Andre Silva", foto=None)
    b = G(Parlamentar, nome_completo="Bartolomeu Gusmao", foto=None)
    c = G(Parlamentar, nome_completo="Camila Carla", foto=None)
    return a, b, c


def test_list_all(some_parliamentarians, app):
    response = app.get('/parlamentares/parlamentar/')
    assert response.status_code == 200

    for x in some_parliamentarians:
        assert x.nome_completo in response.content


def test_list_filtered_by_capital_letter(some_parliamentarians, app):
    response = app.get('/parlamentares/parlamentar/?nome_completo=B')
    assert response.status_code == 200

    decoded_content = response.content.decode('utf-8')
    a, b, c = some_parliamentarians
    assert a.nome_completo not in decoded_content
    assert b.nome_completo in decoded_content
    assert c.nome_completo not in decoded_content
