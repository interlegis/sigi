import pytest

from sigi.apps.casas.test_casas import some_parliaments
from sigi.apps.parlamentares.test_parlamentares import some_parlamentarians
from sigi.testutils import pdf_text


@pytest.mark.parametrize("url, some_entries, form_action, name_attr, verbose_name_plural", [
    ('/parlamentares/parlamentar/', some_parlamentarians, 'adiciona_parlamentar', 'nome_completo', 'Parlamentares'),
    ('/casas/casalegislativa/',     some_parliaments,     'adicionar_casas',      'nome',          'Casas Legislativas'),
])
def test_add_to_cart(url, some_entries, form_action, name_attr, verbose_name_plural, app, live_server):

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
