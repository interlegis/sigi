# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from sigi.apps.utils import SearchField

class UnidadeFederativa(models.Model):
    """ Modelo que representa um estado brasileiro
    """
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
    # Campo de busca em caixa baixa sem acento
    search_text = SearchField(field_names=['nome'])
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
    """ Modelo para representar as cidades brasileiras
    """
    codigo_ibge = models.PositiveIntegerField(
        u'código IBGE',
        primary_key=True,
        unique=True,
        help_text='Código do município segundo IBGE.'
    )

    # agrupamento baseado em similaridades econômicas e sociais
    codigo_mesorregiao = models.PositiveIntegerField(
        u'código mesorregião',
        blank=True,
        null=True
    )
    # agrupamento baseado em similaridades econômicas e sociais
    codigo_microrregiao = models.PositiveIntegerField(
        u'código microrregião',
        blank=True,
        null=True
    )

    # codio designado pelo Tribunal Superior Eleitoral
    codigo_tse = models.PositiveIntegerField(
        u'código TSE',
        unique=True,
        null=True,
        help_text='Código do município segundo TSE.'
    )
    nome = models.CharField(max_length=50)
    search_text = SearchField(field_names=['nome', 'uf'])
    uf = models.ForeignKey(UnidadeFederativa, verbose_name='UF')
    # verdadeiro se o município é capital do estado
    is_capital = models.BooleanField('capital')
    populacao = models.PositiveIntegerField(u'população')
    populacao.list_filter_range = [10000, 100000, 1000000]
    is_polo = models.BooleanField(u'pólo')
    data_criacao = models.DateField(u'data de criação do município', null=True, blank=True)

    # posição geográfica do município
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
    """ Modelo genérico para agrupar telefones dos modulos do sistema
    """
    TELEFONE_CHOICES = (
        ('F', 'Fixo'),
        ('M', 'Móvel'),
        ('X', 'Fax'),
        ('I', 'Indefinido'),
    )
    numero = models.CharField(
        'número',
        max_length=64, # TODO: diminuir tamanho de campo após migração de dados
        help_text='Exemplo: <em>(31)8851-9898</em>.',
    )
    tipo = models.CharField(
        max_length=1,
        choices=TELEFONE_CHOICES,
        default= 'I' 
    )
    nota = models.CharField(max_length=70, null=True, blank=True)
    ult_alteracao = models.DateTimeField(u'Última alteração', null=True, blank=True, editable=False, auto_now=True) 

    # guarda o tipo do objeto (classe) vinculado a esse registro
    content_type = models.ForeignKey(ContentType)
    # identificador do registro na classe vinculado a esse registro
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('numero',)
        unique_together = ('numero', 'tipo')

    def __unicode__(self):
        return unicode(self.numero)

class Contato(models.Model):
    """ Modelo generico para registrar contatos vinculados aos
    modulos do sistema
    """
    nome = models.CharField('nome completo', max_length=120)
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

    # guarda o tipo do objeto (classe) vinculado a esse registro
    content_type = models.ForeignKey(ContentType)
    # identificador do registro na classe vinculado a esse registro
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('nome',)
        verbose_name = 'contato Interlegis'
        verbose_name_plural = 'contatos Interlegis'

    def __unicode__(self):
        return self.nome

class Endereco(models.Model):
    TIPO_CHOICES = (
      ('aeroporto','Aeroporto'),
      ('alameda','Alameda'),
      ('area',u'Área'),
      ('avenida','Avenida'),
      ('campo','Campo'),
      ('chacara',u'Chácara'),
      ('colonia',u'Colônia'),
      ('condominio',u'Condomínio'),
      ('conjunto','Conjunto'),
      ('distrito','Distrito'),
      ('esplanada','Esplanada'),
      ('estacao',u'Estação'),
      ('estrada','Estrada'),
      ('favela','Favela'),
      ('fazenda','Fazenda'),
      ('feira','Feira'),
      ('jardim','Jardim'),
      ('ladeira','Ladeira'),
      ('lago','Lago'),
      ('lagoa','Lagoa'),
      ('largo','Largo'),
      ('loteamento','Loteamento'),
      ('morro','Morro'),
      ('nucleo',u'Núcleo'),
      ('parque','Parque'),
      ('passarela','Passarela'),
      ('patio',u'Pátio'),
      ('praca',u'Praça'),
      ('quadra','Quadra'),
      ('recanto','Recanto'),
      ('residencial','Residencial'),
      ('rodovia','Rodovia'),
      ('rua','Rua'),
      ('setor','Setor'),
      ('sitio',u'Sítio'),
      ('travessa','Travessa'),
      ('trecho','Trecho'),
      ('trevo','Trevo'),
      ('vale','Vale'),
      ('vereda','Vereda'),
      ('via','Via'),
      ('viaduto','Viaduto'),
      ('viela','Viela'),
      ('vila','Vila'),
      ('outro','Outro'),
    )

    # tipo do endereço obtido no site dos correios
    tipo = models.CharField(max_length=15,choices=TIPO_CHOICES)
    logradouro = models.CharField(
        max_length=100,
    )
    logradouro.alphabetic_filter = True
    numero= models.CharField(max_length=15, blank=True)
    complemento= models.CharField(max_length=15, blank=True)
    # campo de texto livre
    referencia = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)

    cep = models.CharField(
        'CEP',
        max_length=9,
        blank=True,
        null=True,
        help_text="Formato: <em>XXXXX-XXX</em>."
    )

    municipio = models.ForeignKey(
        Municipio,
        verbose_name='município',
        blank=True,
        null=True,
    )
    municipio.uf_filter = True

    # guarda o tipo do objeto (classe) vinculado a esse registro
    content_type = models.ForeignKey(ContentType)
    # identificador do registro na classe vinculado a esse registro
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('logradouro', 'numero')
        verbose_name = u'endereço'
        verbose_name_plural = u'endereços'

    def __unicode__(self):
        return self.tipo + ' ' + self.logradouro + ', ' + self.numero \
               + ' ' + self.complemento + ' - ' + self.bairro

