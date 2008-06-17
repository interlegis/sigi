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
        help_text='Código do estado segundo IBGE.'
    )
    nome = models.CharField(max_length=25)
    sigla = models.CharField(max_length=2, help_text="Exemplo: <em>MG</em>.")
    regiao = models.CharField(max_length=2, choices=REGIAO_CHOICES)
    populacao = models.PositiveIntegerField('população')

    class Meta:
        ordering = ('nome',)
        verbose_name = 'Unidade Federativa'
        verbose_name_plural = 'Unidades Federativas'

    class Admin:
        list_display = ('codigo_ibge', 'nome', 'sigla')
        list_display_links = ('codigo_ibge', 'nome', 'sigla')
        search_fields = ('codigo_ibge', 'nome', 'sigla')

    def __unicode__(self):
        return self.nome

class Municipio(models.Model):
    codigo_ibge = models.PositiveIntegerField(
        u'código IBGE',
        primary_key=True,
        help_text='Código do município segundo IBGE.'
    )
    codigo_mesorregiao = models.PositiveIntegerField(
        u'código mesorregião',
    )
    codigo_microrregiao = models.PositiveIntegerField(
        u'código microrregião',
    )
    nome = models.CharField(max_length=50)
    uf = models.ForeignKey(UnidadeFederativa, verbose_name='UF')
    is_capital = models.BooleanField('capital')
    populacao = models.PositiveIntegerField(u'população')
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

    class Admin:
        list_display = ('codigo_ibge', 'nome', 'uf')
        list_display_links = ('codigo_ibge', 'nome')
        list_filter = ('uf',)
        search_fields = ('codigo_ibge', 'nome', 'uf')

    def __unicode__(self):
        return self.nome

    def get_google_maps_url(self):
        return "http://maps.google.com.br/maps/mm?ie=UTF8&hl=pt-BR&t=h&ll=%s,%s&spn=1.61886,1.812744&z=9&source=embed" % \
            (self.latitude, self.longitude)

class Telefone(models.Model):
    TELEFONE_CHOICES = (
        ('F', 'Fixo'),
        ('M', 'Móvel'),
        ('X', 'Fax'),
    )
    codigo_ddd = models.CharField(
        'código DDD',
        max_length=2,
        help_text='Exemplo: <em>31</em>.'
    )
    numero = models.CharField(
        'número',
        max_length=9,
        help_text='Formato: <em>XXXX-XXXX</em>.'
    )
    tipo = models.CharField(
        max_length=1,
        choices=TELEFONE_CHOICES,
        radio_admin=True
    )
    nota = models.CharField(max_length=70, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('codigo_ddd', 'numero')
        unique_together = ('codigo_ddd', 'numero', 'tipo')

    class Admin:
        list_display = ('codigo_ddd', 'numero', 'tipo', 'nota')
        list_display_links = ('codigo_ddd', 'numero')
        list_filter = ('codigo_ddd',)
        search_fields = ('codigo_ddd', 'numero', 'tipo', 'nota')

    def __unicode__(self):
        return "(%s) %s" % (self.codigo_ddd, self.numero)

class Contato(models.Model):
    nome = models.CharField('nome completo', max_length=60)
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

    class Admin:
        list_display = ('nome', 'nota', 'casa_legislativa')
        list_display_links = ('nome',)

    def __unicode__(self):
        return self.nome
