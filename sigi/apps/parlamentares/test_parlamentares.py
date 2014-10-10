# -*- coding: utf-8 -*-
import pytest
from django_dynamic_fixture import G

from sigi.apps.parlamentares.models import Parlamentar


pytestmark = pytest.mark.django_db


@pytest.fixture
def some_parlamentarians():
    a = G(Parlamentar, nome_completo=u"Andre Silva", foto=None)
    b = G(Parlamentar, nome_completo=u"Bartolomeu Gusmao", foto=None)
    c = G(Parlamentar, nome_completo=u"Camila Carla", foto=None)
    return a, b, c


def test_list(some_parlamentarians, admin_client):
    response = admin_client.get('/parlamentares/parlamentar', follow=True)
    assert response.status_code == 200

    decoded_content = response.content.decode('utf-8')
    for x in some_parlamentarians:
        assert x.nome_completo in decoded_content


def test_list_filtered_by_capital_letter(some_parlamentarians, admin_client):
    response = admin_client.get('/parlamentares/parlamentar/?nome_completo=B', follow=True)
    assert response.status_code == 200

    decoded_content = response.content.decode('utf-8')
    a, b, c = some_parlamentarians
    assert a.nome_completo not in decoded_content
    assert b.nome_completo in decoded_content
    assert c.nome_completo not in decoded_content
