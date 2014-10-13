# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _

from sigi.apps.convenios.models import Projeto


class Desembolso(models.Model):
    projeto = models.ForeignKey(Projeto, verbose_name=_(u'Projeto'))
    descricao = models.CharField(_(u'Descrição da despesa'), max_length=100)
    data = models.DateField(_(u'Data do desembolso'))
    valor_reais = models.DecimalField(_(u'Valor em R$'), max_digits=18, decimal_places=2)
    valor_dolar = models.DecimalField(_(u'Valor em US$'), max_digits=18, decimal_places=2)

    class Meta:
        verbose_name = _(u'Desembolso')
        verbose_name_plural = _(u'Desembolsos')

    def __unicode__(self):
        return u"%s (US$ %s)" % (self.descricao, self.valor_dolar)
