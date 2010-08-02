# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class UnidadeFederativa(models.Model):
    REGIAO_CHOICES = (
        ('SL', 'Sul'),
        ('SD', 'Sudeste'),
        ('CO', 'Centro-Oeste'),
        ('NE', 'Nordeste'),
        ('NO', 'Norte'),
    )
    codigo_ibge = models.PositiveIntegerField(
        u'código IBGE',
        primary_key=True,
        unique=True,
        help_text='Código do estado segundo IBGE.'
    )
    nome = models.CharField(max_length=25)
    sigla = models.CharField(
        max_length=2,
        unique=True,
        help_text="Exemplo: <em>MG</em>.",
    )
    regiao = models.CharField('região', max_length=2, choices=REGIAO_CHOICES)
    populacao = models.PositiveIntegerField('população')
    populacao.list_filter_range = [100000, 1000000, 10000000]

    class Meta:
        ordering = ('nome',)
        verbose_name = 'Unidade Federativa'
        verbose_name_plural = 'Unidades Federativas'

    def __unicode__(self):
        return self.nome

class Municipio(models.Model):
    codigo_ibge = models.PositiveIntegerField(
        u'código IBGE',
        primary_key=True,
        unique=True,
        help_text='Código do município segundo IBGE.'
    )
    codigo_mesorregiao = models.PositiveIntegerField(
        u'código mesorregião',
        blank=True,
        null=True
    )
    codigo_microrregiao = models.PositiveIntegerField(
        u'código microrregião',
        blank=True,
        null=True
    )
    codigo_tse = models.PositiveIntegerField(
        u'código TSE',
        unique=True,
        null=True,
        help_text='Código do município segundo TSE.'
    )
    nome = models.CharField(max_length=50)
    uf = models.ForeignKey(UnidadeFederativa, verbose_name='UF')
    is_capital = models.BooleanField('capital')
    populacao = models.PositiveIntegerField(u'população')
    populacao.list_filter_range = [10000, 100000, 1000000]
    is_polo = models.BooleanField(u'pólo')
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        help_text='Exemplo: <em>-20,464</em>.'
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        help_text='Exemplo: <em>-45,426</em>.'
    )

    class Meta:
        ordering = ('nome', 'codigo_ibge')
        verbose_name = 'município'
        verbose_name_plural = 'municípios'

    def __unicode__(self):
        return "%s - %s" % (self.nome, self.uf)

    def get_google_maps_url(self):
        return "http://maps.google.com.br/maps/mm?ie=UTF8&hl=pt-BR&t=h&ll=%s,%s&spn=1.61886,1.812744&z=9&source=embed" % \
            (self.latitude, self.longitude)

class Telefone(models.Model):
    TELEFONE_CHOICES = (
        ('F', 'Fixo'),
        ('M', 'Móvel'),
        ('X', 'Fax'),
        ('I', 'Indefinido'),
    )
    codigo_area = models.CharField(
        'código de área',
        max_length=4,
        help_text='Exemplo: <em>31</em>.',
        blank=True
    )
    numero = models.CharField(
        'número',
        max_length=64, # TODO: diminuir tamanho de campo após migração de dados
        help_text='Somente números.'
    )
    tipo = models.CharField(
        max_length=1,
        choices=TELEFONE_CHOICES,
    )
    nota = models.CharField(max_length=70, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('codigo_area', 'numero')
        # desabilitado para facilitar a migração de dados
        # TODO: voltar quando estiver em produção
        #unique_together = ('codigo_area', 'numero', 'tipo')

    def __unicode__(self):
        if self.codigo_area:
            return "(%s) %s" % (unicode(self.codigo_area), unicode(self.numero))
        else:
            return unicode(self.numero)

class Contato(models.Model):
    nome = models.CharField('nome completo', max_length=60)
    nome.alphabetic_filter = True
    nota = models.CharField(max_length=70, blank=True)

    email = models.EmailField('e-mail', blank=True)
    telefones = generic.GenericRelation(Telefone)

    municipio = models.ForeignKey(
        Municipio,
        verbose_name='município',
        blank=True,
        null=True,
    )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('nome',)
        verbose_name = 'contato Interlegis'
        verbose_name_plural = 'contatos Interlegis'

    def __unicode__(self):
        return self.nome
