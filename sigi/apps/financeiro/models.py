# -*- coding: utf-8 -*-
from django.db import models
from sigi.apps.convenios.models import Projeto


class Desembolso(models.Model):
    projeto = models.ForeignKey(Projeto, verbose_name=u'Projeto')
    descricao = models.CharField(u'Descrição da despesa', max_length=100)
    data = models.DateField(u'Data do desembolso')
    valor_reais = models.DecimalField(u'Valor em R$', max_digits=18, decimal_places=2)
    valor_dolar = models.DecimalField(u'Valor em US$', max_digits=18, decimal_places=2)

    class Meta:
        verbose_name = 'Desembolso'
        verbose_name_plural = 'Desembolsos'

    def __unicode__(self):
        return u"%s (US$ %s)" % (self.descricao, self.valor_dolar)
