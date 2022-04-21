import pytest
from django_dynamic_fixture import G

from sigi.apps.casas.models import Orgao


@pytest.fixture
def some_parliaments():
    return parliaments_from_names(
        [
            "Assembleia Legislativa do Amapa",
            "Camara Municipal de Fortaleza",
            "Camara Legislativa do Distrito Federal",
        ]
    )


def parliaments_from_names(names):
    return [
        G(
            Orgao,
            nome=name,
            foto=None,
        )
        for name in names
    ]
