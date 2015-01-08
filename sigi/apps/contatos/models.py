# -*- coding: utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext as _

from sigi.apps.utils import SearchField


class UnidadeFederativa(models.Model):

    """ Modelo que representa um estado brasileiro
    """
    REGIAO_CHOICES = (
        ('SL', _(u'Sul')),
        ('SD', _(u'Sudeste')),
        ('CO', _(u'Centro-Oeste')),
        ('NE', _(u'Nordeste')),
        ('NO', _(u'Norte')),
    )
    codigo_ibge = models.PositiveIntegerField(
        u'código IBGE',
        primary_key=True,
        unique=True,
        help_text=_(u'Código do estado segundo IBGE.')
    )
    nome = models.CharField(_(u'Nome UF'), max_length=25)
    # Campo de busca em caixa baixa sem acento
    search_text = SearchField(field_names=['nome'])
    sigla = models.CharField(
        max_length=2,
        unique=True,
        help_text=_(u"Exemplo") + ": <em>MG</em>.",
    )
    regiao = models.CharField(_(u'região'), max_length=2, choices=REGIAO_CHOICES)
    populacao = models.PositiveIntegerField(_(u'população'))

    class Meta:
        ordering = (_(u'nome'),)
        verbose_name = _(u'Unidade Federativa')
        verbose_name_plural = _(u'Unidades Federativas')

    def __unicode__(self):
        return self.nome


class Municipio(models.Model):

    """ Modelo para representar as cidades brasileiras
    """
    codigo_ibge = models.PositiveIntegerField(
        _(u'código IBGE'),
        primary_key=True,
        unique=True,
        help_text=_(u'Código do município segundo IBGE.')
    )

    # agrupamento baseado em similaridades econômicas e sociais
    codigo_mesorregiao = models.PositiveIntegerField(
        _(u'código mesorregião'),
        blank=True,
        null=True
    )
    # agrupamento baseado em similaridades econômicas e sociais
    codigo_microrregiao = models.PositiveIntegerField(
        _(u'código microrregião'),
        blank=True,
        null=True
    )

    # codio designado pelo Tribunal Superior Eleitoral
    codigo_tse = models.PositiveIntegerField(
        _(u'código TSE'),
        unique=True,
        null=True,
        help_text=_(u'Código do município segundo TSE.')
    )
    nome = models.CharField(max_length=50)
    search_text = SearchField(field_names=[_(u'nome'), _(u'uf')])
    uf = models.ForeignKey(UnidadeFederativa, verbose_name=_(u'UF'))
    # verdadeiro se o município é capital do estado
    is_capital = models.BooleanField(_(u'capital'), default=False)
    populacao = models.PositiveIntegerField(_(u'população'))
    populacao.list_filter_range = [10000, 100000, 1000000]
    is_polo = models.BooleanField(_(u'pólo'), default=False)
    data_criacao = models.DateField(_(u'data de criação do município'), null=True, blank=True)

    # posição geográfica do município
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        help_text=_(u'Exemplo') + ': <em>-20,464</em>.'
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        help_text=_(u'Exemplo') + ': <em>-45,426</em>.'
    )

    idh = models.DecimalField(_(u'IDH'), help_text=_(u'Índice de desenvolvimento Humano'), max_digits=4, decimal_places=3,
                              validators=[MinValueValidator(0), MaxValueValidator(1)])
    idh.list_filter_range = [0.500, 0.800]

    pib_total = models.DecimalField(_(u'PIB total'), max_digits=18, decimal_places=3, blank=True, null=True)
    pib_percapita = models.DecimalField(_(u'PIB per capita'), max_digits=18, decimal_places=3, blank=True, null=True)
    pib_ano = models.IntegerField(_(u'Ano de apuração do PIB'), blank=True, null=True)

    class Meta:
        ordering = ('nome', 'codigo_ibge')
        verbose_name = _(u'município')
        verbose_name_plural = _(u'municípios')

    def __unicode__(self):
        return "%s - %s" % (self.nome, self.uf)

    def get_google_maps_url(self):
        return "http://maps.google.com.br/maps/mm?ie=UTF8&hl=pt-BR&t=h&ll=%s,%s&spn=1.61886,1.812744&z=9&source=embed" % \
            (self.latitude, self.longitude)


class Telefone(models.Model):

    """ Modelo genérico para agrupar telefones dos modulos do sistema
    """
    TELEFONE_CHOICES = (
        ('F', _(u'Fixo')),
        ('M', _(u'Móvel')),
        ('X', _(u'Fax')),
        ('I', _(u'Indefinido')),
    )
    numero = models.CharField(
        _(u'número'),
        max_length=64,  # TODO: diminuir tamanho de campo após migração de dados
        help_text=_(u'Exemplo') + ': <em>(31)8851-9898</em>.',
    )
    tipo = models.CharField(
        max_length=1,
        choices=TELEFONE_CHOICES,
        default='I'
    )
    nota = models.CharField(max_length=70, null=True, blank=True)
    ult_alteracao = models.DateTimeField(_(u'Última alteração'), null=True, blank=True, editable=False, auto_now=True)

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
    nome = models.CharField(_(u'nome completo'), max_length=120)
    nome.alphabetic_filter = True
    nota = models.CharField(max_length=70, blank=True)

    email = models.EmailField(_(u'e-mail'), blank=True)
    telefones = generic.GenericRelation(Telefone)

    municipio = models.ForeignKey(
        Municipio,
        verbose_name=_(u'município'),
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
        verbose_name = _(u'contato Interlegis')
        verbose_name_plural = _(u'contatos Interlegis')

    def __unicode__(self):
        return self.nome


class Endereco(models.Model):
    TIPO_CHOICES = (
        ('aeroporto', _(u'Aeroporto')),
        ('alameda', _(u'Alameda')),
        ('area', _(u'Área')),
        ('avenida', _(u'Avenida')),
        ('campo', _(u'Campo')),
        ('chacara', _(u'Chácara')),
        ('colonia', _(u'Colônia')),
        ('condominio', _(u'Condomínio')),
        ('conjunto', _(u'Conjunto')),
        ('distrito', _(u'Distrito')),
        ('esplanada', _(u'Esplanada')),
        ('estacao', _(u'Estação')),
        ('estrada', _(u'Estrada')),
        ('favela', _(u'Favela')),
        ('fazenda', _(u'Fazenda')),
        ('feira', _(u'Feira')),
        ('jardim', _(u'Jardim')),
        ('ladeira', _(u'Ladeira')),
        ('lago', _(u'Lago')),
        ('lagoa', _(u'Lagoa')),
        ('largo', _(u'Largo')),
        ('loteamento', _(u'Loteamento')),
        ('morro', _(u'Morro')),
        ('nucleo', _(u'Núcleo')),
        ('parque', _(u'Parque')),
        ('passarela', _(u'Passarela')),
        ('patio', _(u'Pátio')),
        ('praca', _(u'Praça')),
        ('quadra', _(u'Quadra')),
        ('recanto', _(u'Recanto')),
        ('residencial', _(u'Residencial')),
        ('rodovia', _(u'Rodovia')),
        ('rua', _(u'Rua')),
        ('setor', _(u'Setor')),
        ('sitio', _(u'Sítio')),
        ('travessa', _(u'Travessa')),
        ('trecho', _(u'Trecho')),
        ('trevo', _(u'Trevo')),
        ('vale', _(u'Vale')),
        ('vereda', _(u'Vereda')),
        ('via', _(u'Via')),
        ('viaduto', _(u'Viaduto')),
        ('viela', _(u'Viela')),
        ('vila', _(u'Vila')),
        ('outro', _(u'Outro')),
    )

    # tipo do endereço obtido no site dos correios
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    logradouro = models.CharField(
        max_length=100,
    )
    logradouro.alphabetic_filter = True
    numero = models.CharField(max_length=15, blank=True)
    complemento = models.CharField(max_length=15, blank=True)
    # campo de texto livre
    referencia = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)

    cep = models.CharField(
        _(u'CEP'),
        max_length=9,
        blank=True,
        null=True,
        help_text=_(u"Formato") + ": <em>XXXXX-XXX</em>."
    )

    municipio = models.ForeignKey(
        Municipio,
        verbose_name=_(u'município'),
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
        verbose_name = _(u'endereço')
        verbose_name_plural = _(u'endereços')

    def __unicode__(self):
        return self.tipo + ' ' + self.logradouro + ', ' + self.numero \
            + ' ' + self.complemento + ' - ' + self.bairro
