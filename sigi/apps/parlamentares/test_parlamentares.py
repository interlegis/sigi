# -*- coding: utf-8 -*-
import pytest
from django_dynamic_fixture import G

from sigi.apps.parlamentares.models import Parlamentar
from sigi.testutils import pdf_text


pytestmark = pytest.mark.django_db


@pytest.fixture
def some_parlamentarians():
    a = G(Parlamentar, nome_completo="Andre Silva", foto=None)
    b = G(Parlamentar, nome_completo="Bartolomeu Gusmao", foto=None)
    c = G(Parlamentar, nome_completo="Camila Carla", foto=None)
    return a, b, c


def test_list_all(some_parlamentarians, admin_user, app):
    response = app.get('/parlamentares/parlamentar/', auto_follow=True, user=admin_user.username)
    assert response.status_code == 200

    for x in some_parlamentarians:
        assert x.nome_completo in response.content


def test_list_filtered_by_capital_letter(some_parlamentarians, admin_client):
    response = admin_client.get('/parlamentares/parlamentar/?nome_completo=B', follow=True)
    assert response.status_code == 200

    decoded_content = response.content.decode('utf-8')
    a, b, c = some_parlamentarians
    assert a.nome_completo not in decoded_content
    assert b.nome_completo in decoded_content
    assert c.nome_completo not in decoded_content


def test_add_to_cart(some_parlamentarians, admin_user, app):
    res = app.get('/parlamentares/parlamentar/', auto_follow=True, user=admin_user.username)
    assert res.status_code == 200

    a, b, c = some_parlamentarians

    form = res.forms['changelist-form']
    form['_selected_action'] = [a.pk, b.pk]  # Andre and Bartolomeu
    form['action'] = 'adiciona_parlamentar'
    res = form.submit()
    "2 Parlamentares adicionados" in res.content
    res = app.get('/parlamentares/parlamentar/carrinho/', auto_follow=True, user=admin_user.username)

    def right_people_present(content):
        assert a.nome_completo in content
        assert b.nome_completo in content
        assert c.nome_completo not in content

    right_people_present(res.content)
    'Formato da Etiqueta' in res.content
    'Gerar Etiqueta' in res.content

    labels_form = res.forms['generate_labels']
    res = labels_form.submit()
    assert res.content_type == 'application/pdf'
    text = pdf_text(res)
    right_people_present(text)
