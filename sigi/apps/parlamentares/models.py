# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic

class Partido(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)

    class Meta:
        ordering = ('nome',)

    class Admin:
        list_display = ('nome', 'sigla')
        list_display_links = ('nome', 'sigla')

    def __unicode__(self):
        return '%s (%s)' % (self.nome, self.sigla)

class Parlamentar(models.Model):
    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    )
    SUPLENCIA_CHOICES = (
        ('T', 'Titular'),
        ('S', 'Suplente'),
    )
    nome_completo = models.CharField(max_length=60)
    nome_parlamentar = models.CharField(max_length=35, blank=True)
    foto = models.ImageField(
        upload_to='fotos/parlamentares',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        radio_admin=True
    )
    data_nascimento = models.DateField(
        'data de nascimento',
        blank=True,
        null=True,
    )
    partido = models.ForeignKey(Partido)
    inicio_mandato = models.DateField('início de mandato')
    inicio_mandato = models.DateField('fim de mandato')
    is_afastado = models.BooleanField(
        'Afastado',
        default=False,
        help_text='Marque caso parlamentar não esteja ativo'
    )
    suplencia = models.CharField(
        'suplência',
        max_length=1,
        choices=SUPLENCIA_CHOICES,
        radio_admin=True
    )
    logradouro = models.CharField(max_length=100)
    bairro = models.CharField(max_length=40)
    cidade = models.ForeignKey('localidades.Municipio')
    cep = models.CharField(
        'CEP',
        max_length=9,
        help_text="Formato: <em>XXXXX-XXX</em>."
    )
    telefones = generic.GenericRelation('telefones.Telefone')
    pagina_web = models.URLField('página web')
    email = models.EmailField('e-mail')

    class Meta:
        ordering = ('nome_completo',)
        verbose_name_plural = 'parlamentares'

    class Admin:
        list_display = ('nome_completo', 'nome_parlamentar', 'sexo', 'partido',
                        'suplencia')
        list_display_links = ('nome_completo', 'nome_parlamentar')
        list_filter = ('sexo', 'suplencia', 'partido')
