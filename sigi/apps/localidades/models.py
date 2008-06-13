# -*- coding: utf-8 -*-
from django.db import models

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
