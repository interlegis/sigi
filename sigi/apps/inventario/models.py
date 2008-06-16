# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic

class Fornecedor(models.Model):
    nome = models.CharField(max_length=40)
    email = models.EmailField('e-mail', blank=True)
    pagina_web = models.URLField('página web', blank=True)
    telefones = generic.GenericRelation('telefones.Telefone')

    class Meta:
        ordering = ('nome',)
        verbose_name_plural = 'fornecedores'

    class Admin:
        list_display = ('id', 'nome')

    def __unicode__(self):
        return self.nome

class Fabricante(models.Model):
    nome = models.CharField(max_length=40)

    class Meta:
        ordering = ('nome',)

    class Admin:
        list_display = ('id', 'nome')

    def __unicode__(self):
        return self.nome

class TipoEquipamento(models.Model):
    tipo = models.CharField(max_length=40)

    class Meta:
        ordering = ('tipo',)
        verbose_name = 'tipo de equipamento'
        verbose_name_plural = 'tipos de equipamentos'

    class Admin:
        list_display = ('id', 'tipo')

    def __unicode__(self):
        return self.tipo

class ModeloEquipamento(models.Model):
    tipo = models.ForeignKey(
        TipoEquipamento,
        verbose_name='tipo de equipamento'
    )
    modelo = models.CharField(max_length=30)

    class Meta:
        ordering = ('modelo',)
        verbose_name = 'modelo de equipamento'
        verbose_name_plural = 'modelos de equipamentos'

    class Admin:
        list_display = ('id', 'tipo', 'modelo')

    def __unicode__(self):
        return self.modelo

class Equipamento(models.Model):
    fabricante = models.ForeignKey(Fabricante)
    modelo = models.ForeignKey(ModeloEquipamento)

    class Meta:
        unique_together = (('fabricante', 'modelo'),)

    class Admin:
        ordering = ('fabricante', 'tipo', 'modelo')
        list_display = ('id', 'tipo', 'modelo', 'fabricante')
        list_filter  = ('tipo', 'fabricante')

    def __unicode__(self):
        return self.id

class Bem(models.Model):
    casa_legislativa = models.ForeignKey('casas.CasaLegislativa')
    equipamento = models.ForeignKey(Equipamento)
    fornecedor = models.ForeignKey(Fornecedor)
    num_serie = models.CharField(
        'número de série',
        max_length=50,
        help_text='Número fornecido pelo fabricante.',
        unique=True
    )
    num_tombamento = models.CharField(
        'número de tombamento',
        max_length=50,
        help_text='Número fornecido pelo Interlegis.',
        unique=True
    )

    class Meta:
        verbose_name_plural = 'bens'

    class Admin:
        ordering = ('casa_legislativa', 'fornecedor', 'equipamento')
        list_display = ('equipamento', 'fornecedor', 'num_serie',
                        'num_tombamento', 'casa_legislativa')

    def __unicode__(self):
        return '%s (%s)' % (self.equipamento, self.casa_legislativa)
