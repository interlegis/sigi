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
    nome = models.CharField(
        max_length=60,
        help_text='Exemplo: <em>Câmara Municipal de Pains</em>.'
    )
    sigla = models.CharField(
        max_length=30,
        help_text='Forneça apenas se a Casa Legislativa indicar um. '
                  'Exemplo: <em>cmpains</em>.',
        blank=True
    )
    tipo = models.CharField(max_length=2, choices=CASA_CHOICES, default='CM')
    cnpj = models.CharField('CNPJ', max_length=18, blank=True)

    logradouro = models.CharField(
        max_length=100,
        help_text='Avenida, rua, praça, jardim, parque...'
    )
    bairro = models.CharField(max_length=40, blank=True)
    municipio = models.ForeignKey(
        'contatos.Municipio',
        verbose_name='município'
    )
    cep = models.CharField(max_length=9)
    email = models.EmailField('e-mail', blank=True)
    pagina_web = models.URLField(
        u'página web',
        help_text='Exemplo: <em>http://www.camarapains.mg.gov.br</em>.',
        blank=True
    )
    telefones = generic.GenericRelation('contatos.Telefone')

    foto = models.ImageField(
        upload_to='imagens/casas',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    historico = models.TextField(u'histórico', blank=True)

    contatos = generic.GenericRelation('contatos.Contato')

    class Meta:
        ordering = ('nome',)
        verbose_name = 'Casa Legislativa'
        verbose_name_plural = 'Casas Legislativas'

    def __unicode__(self):
        return self.nome
