import pytest
from django_dynamic_fixture import G

from sigi.apps.casas.models import CasaLegislativa


@pytest.fixture
def some_parliaments():
    return parliaments_from_names([
        "Assembleia Legislativa do Amapa",
        "Camara Municipal de Fortaleza",
        "Camara Legislativa do Distrito Federal",
    ])


def parliaments_from_names(names):
    return [G(CasaLegislativa, nome=name, foto=None, gerente_contas=None,
              pesquisador=None,) for name in names]
