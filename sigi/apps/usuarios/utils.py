# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.utils.translation import ugettext_lazy as _

UF = [
    (u'AC', u'Acre'),
    (u'AL', u'Alagoas'),
    (u'AP', u'Amapá'),
    (u'AM', u'Amazonas'),
    (u'BA', u'Bahia'),
    (u'CE', u'Ceará'),
    (u'DF', u'Distrito Federal'),
    (u'ES', u'Espírito Santo'),
    (u'GO', u'Goiás'),
    (u'MA', u'Maranhão'),
    (u'MT', u'Mato Grosso'),
    (u'MS', u'Mato Grosso do Sul'),
    (u'MG', u'Minas Gerais'),
    (u'PR', u'Paraná'),
    (u'PB', u'Paraíba'),
    (u'PA', u'Pará'),
    (u'PE', u'Pernambuco'),
    (u'PI', u'Piauí'),
    (u'RJ', u'Rio de Janeiro'),
    (u'RN', u'Rio Grande do Norte'),
    (u'RS', u'Rio Grande do Sul'),
    (u'RO', u'Rondônia'),
    (u'RR', u'Roraima'),
    (u'SC', u'Santa Catarina'),
    (u'SE', u'Sergipe'),
    (u'SP', u'São Paulo'),
    (u'TO', u'Tocantins'),
    (u'EX', u'Exterior'),
]

YES_NO_CHOICES = [(None, _(u'----')), (False, _(u'Não')), (True, _(u'Sim'))]


def str2bool(v):
    return v in (u'Sim', u'True')


SEXO_CHOICES = [(u'M', _(u'Masculino')), (u'F', _(u'Feminino'))]


def from_to(start, end):
    return range(start, end + 1)


def make_pagination(index, num_pages):
    PAGINATION_LENGTH = 10
    if num_pages <= PAGINATION_LENGTH:
        return from_to(1, num_pages)
    else:
        if index - 1 <= 5:
            tail = [num_pages - 1, num_pages]
            head = from_to(1, PAGINATION_LENGTH - 3)
        else:
            if index + 1 >= num_pages - 3:
                tail = from_to(index - 1, num_pages)
            else:
                tail = [index - 1, index, index + 1,
                        None, num_pages - 1, num_pages]
            head = from_to(1, PAGINATION_LENGTH - len(tail) - 1)
        return head + [None] + tail
