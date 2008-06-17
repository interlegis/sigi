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
    cidade = models.ForeignKey('contatos.Municipio')
    cep = models.CharField(
        max_length=9,
        help_text="Formato: <em>XXXXX-XXX</em>."
    )
    email = models.EmailField('e-mail', blank=True)
    pagina_web = models.URLField('página web', blank=True)
    telefones = generic.GenericRelation('contatos.Telefone')

    foto = models.ImageField(
        upload_to='imagens/casas',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    historico = models.TextField('histórico', blank=True)

    contatos = generic.GenericRelation('contatos.Contato')

    class Meta:
        ordering = ('nome',)
        verbose_name = 'Casa Legislativa'
        verbose_name_plural = 'Casas Legislativas'

    class Admin:
        list_display = ('nome', 'email', 'pagina_web')
        list_display_links = ('nome',)

    def __unicode__(self):
        return self.nome
