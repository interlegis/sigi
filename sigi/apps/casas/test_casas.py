import pytest
from django_dynamic_fixture import G

from sigi.apps.casas.models import CasaLegislativa


@pytest.fixture
def some_parliaments():
    a = G(CasaLegislativa, nome="Assembleia Legislativa do Amapa", foto=None, gerente_contas=None,)
    b = G(CasaLegislativa, nome="Camara Municipal de Fortaleza", foto=None, gerente_contas=None,)
    c = G(CasaLegislativa, nome="Camara Legislativa do Distrito Federal", foto=None, gerente_contas=None,)
    return a, b, c
