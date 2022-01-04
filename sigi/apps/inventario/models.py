# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext as _


class Fornecedor(models.Model):
    nome = models.CharField(max_length=40)
    nome.alphabetic_filter = True
    email = models.EmailField(_(u'e-mail'), blank=True)
    pagina_web = models.URLField(_(u'página web'), blank=True)
    telefones = GenericRelation('contatos.Telefone')
    contatos = GenericRelation('contatos.Contato')

    class Meta:
        ordering = ('nome',)
        verbose_name_plural = _(u'fornecedores')

    def __unicode__(self):
        return self.nome


class Fabricante(models.Model):
    nome = models.CharField(max_length=40, unique=True)
    nome.alphabetic_filter = True

    class Meta:
        ordering = ('nome',)

    def __unicode__(self):
        return self.nome


class TipoEquipamento(models.Model):
    tipo = models.CharField(max_length=40)

    class Meta:
        ordering = ('tipo',)
        verbose_name = _(u'tipo de equipamento')
        verbose_name_plural = _(u'tipos de equipamentos')

    def __unicode__(self):
        return self.tipo


class ModeloEquipamento(models.Model):
    tipo = models.ForeignKey(
        TipoEquipamento,
        on_delete=models.PROTECT,
        verbose_name=_(u'tipo de equipamento')
    )
    modelo = models.CharField(max_length=30)

    class Meta:
        ordering = ('modelo',)
        verbose_name = _(u'modelo de equipamento')
        verbose_name_plural = _(u'modelos de equipamentos')

    def __unicode__(self):
        return self.modelo


class Equipamento(models.Model):
    fabricante = models.ForeignKey(
        Fabricante,
        on_delete=models.PROTECT
    )
    modelo = models.ForeignKey(
        ModeloEquipamento,
        on_delete=models.PROTECT
    )

    class Meta:
        unique_together = (('fabricante', 'modelo'),)

    def __unicode__(self):
        return unicode('%s %s %s' % (self.modelo.tipo, self.fabricante.nome,
                                     self.modelo.modelo))


class Bem(models.Model):
    casa_legislativa = models.ForeignKey(
        'casas.Orgao',
        on_delete=models.CASCADE
    )
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT)
    num_serie = models.CharField(
        _(u'número de série'),
        max_length=64,
        help_text=_(u'Número fornecido pelo fabricante.'),
        unique=True
    )
    recebido_por = models.CharField(
        max_length=64,
        blank=True,
        help_text=_(u'Nome de quem recebeu o equipamento.')
    )
    observacoes = models.TextField(_(u'observações'), blank=True)

    class Meta:
        verbose_name_plural = _(u'bens')

    def __unicode__(self):
        return unicode('%s (%s)') % (self.equipamento, self.casa_legislativa)
