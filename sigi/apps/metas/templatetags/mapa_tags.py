# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

from sigi.apps.casas.models import Orgao
from sigi.apps.metas.views import parliament_summary


register = template.Library()


@register.filter(name='map_desc_serv')
def descricao_servicos(casa):
    if not isinstance(casa, Orgao):
        return ""

    summary = parliament_summary(casa)
    result = ''.join('<li>%s</li>' % info for info in summary['info'])
    return mark_safe(result)
descricao_servicos.is_safe = True
