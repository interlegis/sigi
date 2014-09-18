# -*- coding: utf-8 -*-

from django import template
from django.utils.safestring import mark_safe
from sigi.apps.casas.models import CasaLegislativa

register = template.Library()


@register.filter(name='map_desc_serv')
def descricao_servicos(value):
    if not isinstance(value, CasaLegislativa):
        return ""

    result = ""

    for sv in value.servico_set.all():
        result += u'<li>%s ativado em %s</li>' % (sv.tipo_servico.nome, sv.data_ativacao.strftime('%d/%m/%Y'))

    for cv in value.convenio_set.all():
        if (cv.data_retorno_assinatura is None) and (cv.equipada and cv.data_termo_aceite is not None):
            result += u"<li>Equipada em %s pelo %s</li>" % (cv.data_termo_aceite.strftime('%d/%m/%Y'), cv.projeto.sigla)
        if (cv.data_retorno_assinatura is not None) and not (cv.equipada and cv.data_termo_aceite is not None):
            result += u"<li>Conveniada ao %s em %s</li>" % (cv.projeto.sigla, cv.data_retorno_assinatura.strftime('%d/%m/%Y'))
        if (cv.data_retorno_assinatura is not None) and (cv.equipada and cv.data_termo_aceite is not None):
            result += u"<li>Conveniada ao %s em %s e equipada em %s</li>" % (cv.projeto.sigla, cv.data_retorno_assinatura.strftime('%d/%m/%Y'), cv.data_termo_aceite.strftime('%d/%m/%Y'))

    for dg in value.diagnostico_set.all():
        result += u'<li>Diagnosticada no período de %s a %s</li>' % (dg.data_visita_inicio.strftime('%d/%m/%Y') if dg.data_visita_inicio
                                                                     else u"<< sem data inicial >>",
                                                                     dg.data_visita_fim.strftime('%d/%m/%Y') if dg.data_visita_fim
                                                                     else u"<< sem data final >>")

    return mark_safe(result)
descricao_servicos.is_safe = True
