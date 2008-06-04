# -*- coding: utf-8 -*-
from django.db import models

class UnidadeFederativa(models.Model):
    codigo_ibge = models.PositiveIntegerField(
        u'código IBGE',
        primary_key=True,
        help_text='Código do estado segundo IBGE.'
    )
    nome = models.CharField(max_length=25)
    sigla = models.CharField(max_length=2, help_text="Exemplo: <em>MG</em>.")

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
    nome = models.CharField(max_length=50)
    uf = models.ForeignKey(UnidadeFederativa, verbose_name='UF')
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
