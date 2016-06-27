# -*- coding: utf-8 -*-
import pytest

from sigi.apps.casas.test_casas import parliaments_from_names, some_parliaments
from sigi.apps.parlamentares.test_parlamentares import (parliamentarians_from_names,
                                                        some_parliamentarians)
from sigi.testutils import pdf_text


@pytest.mark.parametrize("url, some_entries, form_action, name_attr, verbose_name_plural", [
    ('/parlamentares/parlamentar/', some_parliamentarians, 'adiciona_parlamentar', 'nome_completo', 'Parlamentares'),
    ('/casas/casalegislativa/', some_parliaments, 'adicionar_casas', 'nome', 'Casas Legislativas'),
])
def test_add_to_cart(url, some_entries, form_action, name_attr, verbose_name_plural, app):

    a, b, c = some_entries()

    res = app.get(url)
    assert res.status_code == 200

    form = res.forms['changelist-form']
    form['_selected_action'] = [a.pk, b.pk]  # Andre and Bartolomeu
    form['action'] = form_action
    res = form.submit()
    "2 %s adicionados" % verbose_name_plural in res.content
    res = app.get(url + 'carrinho/')

    def right_people_present(content):
        assert getattr(a, name_attr) in content
        assert getattr(b, name_attr) in content
        assert getattr(c, name_attr) not in content

    right_people_present(res.content)
    'Formato da Etiqueta' in res.content
    'Gerar Etiqueta' in res.content
    labels_form = res.forms['generate_labels']
    res = labels_form.submit()
    assert res.content_type == 'application/pdf'
    text = pdf_text(res)
    right_people_present(text)


@pytest.mark.parametrize("url, some_entries, all_expression", [
    ('/parlamentares/parlamentar/', some_parliamentarians, 'todos os parlamentares', ),
    ('/casas/casalegislativa/', some_parliaments, 'todas as casas', ),
])
def test_no_selection_brings_everyone_to_the_cart(url, some_entries, all_expression, app):

    some_entries()

    res = app.get(url + 'carrinho/')
    assert res.status_code == 200

    msg = 'O carrinho está vazio, sendo assim %s entram na lista para exportação' % all_expression
    assert msg in res.content


@pytest.mark.parametrize("url, generate_entries", [
    ('/parlamentares/parlamentar/', parliamentarians_from_names, ),
    ('/casas/casalegislativa/', parliaments_from_names, ),
])
def test_pagination(url, generate_entries, app, live_server):

    def assert_on_page_1(res):
        assert len(res.pyquery('.result_list tbody tr')) == 100
        assert 'Página 1 de 2' in res.content
        assert '112 itens' in res.content
        assert 'Anterior' not in res.content
        link = res.html.find('a', text='Próxima')
        assert link.attrs['href'] == '?page=2'

    def assert_on_page_2(res):
        assert len(res.pyquery('.result_list tbody tr')) == 12
        assert 'Página 2 de 2' in res.content
        assert '112 itens' in res.content
        assert 'Próxima' not in res.content
        link = res.html.find('a', text='Anterior')
        assert link.attrs['href'] == '?page=1'

    generate_entries(range(112))
    url_cart = url + 'carrinho/'

    res = app.get(url_cart)
    assert res.status_code == 200
    assert_on_page_1(res)

    res = app.get(url_cart + '?page=2')
    assert_on_page_2(res)

    # if the argument is too big we land on the last page
    res = app.get(url_cart + '?page=1000')
    assert_on_page_2(res)

    # if the argument is not a number we land on the first page
    res = app.get(url + 'carrinho/?page=aaaa')
    assert_on_page_1(res)
