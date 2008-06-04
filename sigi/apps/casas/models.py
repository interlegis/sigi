# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic

class CasaLegislativa(models.Model):
    CASA_CHOICES = (
        ('CM', 'Câmara Municipal'),
        ('AL', 'Assembléia Legislativa'),
        ('CD', 'Câmara dos Deputados'),
        ('CT', 'Câmara Distrital'),
        ('SF', 'Senado Federal'),
    )
    nome = models.CharField(max_length=60)
    sigla = models.CharField(max_length=30, blank=True)
    tipo = models.CharField(max_length=2, choices=CASA_CHOICES)
    cnpj = models.CharField('CNPJ', max_length=18)

    logradouro = models.CharField(max_length=100)
    bairro = models.CharField(max_length=40)
    cidade = models.ForeignKey('localidades.Municipio')
    cep = models.CharField(
        max_length=9,
        help_text="Formato: <em>XXXXX-XXX</em>."
    )
    email = models.EmailField('e-mail', blank=True)
    pagina_web = models.URLField('página web', blank=True)
    telefones = generic.GenericRelation('telefones.Telefone')

    foto = models.ImageField(
        upload_to='imagens/fotos/casas',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    historico = models.TextField('histórico', blank=True)

    class Meta:
        ordering = ('nome',)
        verbose_name = 'Casa Legislativa'
        verbose_name_plural = 'Casas Legislativas'

    class Admin:
        list_display = ('nome', 'email', 'pagina_web', 'telefones')
        list_display_links = ('nome',)
        search_fields = ('nome', 'sigla', 'tipo', 'logradouro', 'bairro',
                         'cidade', 'cep', 'email', 'pagina_web', 'telefones')

    def __unicode__(self):
        return self.nome

class ContatoInterlegis(models.Model):
    nome = models.CharField('nome completo', max_length=60)
    casa_legislativa = models.ForeignKey(
        CasaLegislativa,
        verbose_name='Casa Legislativa'
    )
    nota = models.CharField(max_length=70, blank=True)

    email = models.EmailField('e-mail', blank=True)
    telefones = generic.GenericRelation('telefones.Telefone')

    class Meta:
        ordering = ('nome',)
        verbose_name = 'contato Interlegis'
        verbose_name_plural = 'contatos Interlegis'

    class Admin:
        list_display = ('nome', 'nota', 'casa_legislativa')
        list_display_links = ('nome',)

    def __unicode__(self):
        return self.nome
