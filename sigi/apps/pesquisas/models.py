# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ungettext, ugettext_lazy as _
from sigi.forms_builder.forms.models import AbstractForm, AbstractField, AbstractFormEntry, AbstractFieldEntry
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.servidores.models import Servidor

class Pesquisa(AbstractForm):
    class Meta:
        verbose_name = _("Pesquisa")
        verbose_name_plural = _("Pesquisas")

class Pergunta(AbstractField):
    """
    Implements automated field ordering.
    """

    form = models.ForeignKey("Pesquisa", related_name="fields")
    order = models.IntegerField(_("Order"), null=True, blank=True)

    class Meta(AbstractField.Meta):
        ordering = ("order",)

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = self.form.fields.count()
        super(Pergunta, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        fields_after = self.form.fields.filter(order__gte=self.order)
        fields_after.update(order=models.F("order") - 1)
        super(Pergunta, self).delete(*args, **kwargs)

class Formulario(AbstractFormEntry):
    form = models.ForeignKey("Pesquisa", related_name="entries")
    casa_legislativa = models.ForeignKey(CasaLegislativa, verbose_name=u"Casa legislativa")
    #operador = models.ForeignKey(Servidor, verbose_name=u"Operador")
    
    class Meta(AbstractFormEntry.Meta):
        unique_together = ('form', 'casa_legislativa')
    
class Resposta(AbstractFieldEntry):
    entry = models.ForeignKey("Formulario", related_name="fields")