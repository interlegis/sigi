# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _

from sigi.apps.convenios.models import Projeto


class Desembolso(models.Model):
    projeto = models.ForeignKey(
        Projeto, on_delete=models.CASCADE, verbose_name=_("Projeto")
    )
    descricao = models.CharField(_("Descrição da despesa"), max_length=100)
    data = models.DateField(_("Data do desembolso"))
    valor_reais = models.DecimalField(
        _("Valor em R$"), max_digits=18, decimal_places=2
    )
    valor_dolar = models.DecimalField(
        _("Valor em US$"), max_digits=18, decimal_places=2
    )

    class Meta:
        verbose_name = _("Desembolso")
        verbose_name_plural = _("Desembolsos")

    def __unicode__(self):
        return "%s (US$ %s)" % (self.descricao, self.valor_dolar)
