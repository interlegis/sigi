from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext as _

from sigi.apps.utils import SearchField

class UnidadeFederativa(models.Model):
    REGIAO_CHOICES = (
        ('CO', _('Centro-Oeste')),
        ('NE', _('Nordeste')),
        ('NO', _('Norte')),
        ('SD', _('Sudeste')),
        ('SL', _('Sul')),
    )
    codigo_ibge = models.PositiveIntegerField(
        _('código IBGE'),
        primary_key=True,
        unique=True,
        help_text=_('código do estado segundo IBGE.')
    )
    nome = models.CharField(_('nome UF'), max_length=25)
    search_text = SearchField(field_names=['nome'])
    sigla = models.CharField(
        _('sigla'),
        max_length=2,
        unique=True,
        help_text=_(u"Exemplo: <em>MG</em>."),
    )
    regiao = models.CharField(_('região'), max_length=2, choices=REGIAO_CHOICES)
    populacao = models.PositiveIntegerField(_('população'))

    class Meta:
        ordering = ('nome',)
        verbose_name = _('Unidade Federativa')
        verbose_name_plural = _('Unidades Federativas')

    def __str__(self):
        return self.nome

class Mesorregiao(models.Model):
    codigo_ibge = models.PositiveIntegerField(
        _('código IBGE'),
        primary_key=True,
        unique=True,
        help_text=_('código da mesorregião segundo o IBGE')
    )
    uf = models.ForeignKey(
        UnidadeFederativa,
        on_delete=models.CASCADE,
        verbose_name=_('UF')
    )
    nome = models.CharField(_(u"nome mesorregião"), max_length=100)
    search_text = SearchField(field_names=['nome'])

    class Meta:
        ordering = ('uf', 'nome',)
        verbose_name = _('mesorregião')
        verbose_name_plural = _('mesorregiões')

    def __str__(self):
        return self.nome

class Microrregiao(models.Model):
    codigo_ibge = models.PositiveIntegerField(
        _('código IBGE'),
        primary_key=True,
        unique=True,
        help_text=_('código da microrregião segundo o IBGE')
    )
    mesorregiao = models.ForeignKey(
        Mesorregiao,
        on_delete=models.CASCADE,
        verbose_name=_('mesorregião')
    )
    nome = models.CharField(_(u"nome microrregião"), max_length=100)
    search_text = SearchField(field_names=['nome'])

    class Meta:
        ordering = ('nome',)
        verbose_name = _('microrregião')
        verbose_name_plural = _('microrregiões')

    def __str__(self):
        return u"%s (%s)" % (self.nome, self.mesorregiao.nome)

class Municipio(models.Model):
    codigo_ibge = models.PositiveIntegerField(
        _('código IBGE'),
        primary_key=True,
        unique=True,
        help_text=_('código do município segundo IBGE.')
    )

    microrregiao = models.ForeignKey(
        Microrregiao,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('microrregião')
    )

    # codio designado pelo Tribunal Superior Eleitoral
    codigo_tse = models.PositiveIntegerField(
        _('código TSE'),
        unique=True,
        null=True,
        help_text=_('código do município segundo TSE.')
    )
    nome = models.CharField(_('nome'), max_length=50)
    search_text = SearchField(field_names=['nome', 'uf'])
    uf = models.ForeignKey(
        UnidadeFederativa,
        on_delete=models.PROTECT,
        verbose_name=_('UF')
    )
    is_capital = models.BooleanField(_('capital'), default=False)
    populacao = models.PositiveIntegerField(_('população'))
    is_polo = models.BooleanField(_('pólo'), default=False)
    data_criacao = models.DateField(
        _('data de criação do município'),
        null=True,
        blank=True
    )
    latitude = models.DecimalField(
        _('latitude'),
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        help_text=_('Exemplo') + ': <em>-20,464</em>.'
    )
    longitude = models.DecimalField(
        _('longitude'),
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        help_text=_('Exemplo') + ': <em>-45,426</em>.'
    )
    idh = models.DecimalField(
        _('IDH'),
        help_text=_('Índice de Desenvolvimento Humano'),
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    pib_total = models.DecimalField(
        _('PIB total'),
        max_digits=18,
        decimal_places=3,
        blank=True,
        null=True
    )
    pib_percapita = models.DecimalField(
        _('PIB per capita'),
        max_digits=18,
        decimal_places=3,
        blank=True,
        null=True
    )
    pib_ano = models.IntegerField(
        _('ano de apuração do PIB'),
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('nome', 'codigo_ibge')
        verbose_name = _('município')
        verbose_name_plural = _('municípios')

    def __str__(self):
        return "%s - %s" % (self.nome, self.uf)

class Telefone(models.Model):
    TELEFONE_CHOICES = (
        ('F', _('Fixo')),
        ('M', _('Móvel')),
        ('X', _('Fax')),
        ('I', _('Indefinido')),
    )
    numero = models.CharField(
        _('número'),
        max_length=64,  # TODO: diminuir tamanho de campo após migração de dados
        help_text=_('Exemplo: <em>(31)8851-9898</em>.'),
    )
    tipo = models.CharField(
        _('tipo'),
        max_length=1,
        choices=TELEFONE_CHOICES,
        default='I'
    )
    nota = models.CharField(
        _('nota'),
        max_length=70,
        null=True,
        blank=True
    )
    ult_alteracao = models.DateTimeField(
        _('última alteração'),
        null=True,
        blank=True,
        editable=False,
        auto_now=True
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('numero',)
        unique_together = ('numero', 'tipo')
        verbose_name = _('telefone')
        verbose_name_plural = _('telefones')

    def __str__(self):
        return str(self.numero)

class Contato(models.Model):
    nome = models.CharField(_('nome completo'), max_length=120)
    nota = models.CharField(_('nota'), max_length=70, blank=True)
    email = models.EmailField(_('e-mail'), blank=True)
    telefones = GenericRelation(Telefone, verbose_name=_('telefones'))
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('município')
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')

    class Meta:
        ordering = ('nome',)
        verbose_name = _('contato Interlegis')
        verbose_name_plural = _('contatos Interlegis')

    def __str__(self):
        return self.nome

class Endereco(models.Model):
    TIPO_CHOICES = (
        ('aeroporto', _('Aeroporto')),
        ('alameda', _('Alameda')),
        ('area', _('Área')),
        ('avenida', _('Avenida')),
        ('campo', _('Campo')),
        ('chacara', _('Chácara')),
        ('colonia', _('Colônia')),
        ('condominio', _('Condomínio')),
        ('conjunto', _('Conjunto')),
        ('distrito', _('Distrito')),
        ('esplanada', _('Esplanada')),
        ('estacao', _('Estação')),
        ('estrada', _('Estrada')),
        ('favela', _('Favela')),
        ('fazenda', _('Fazenda')),
        ('feira', _('Feira')),
        ('jardim', _('Jardim')),
        ('ladeira', _('Ladeira')),
        ('lago', _('Lago')),
        ('lagoa', _('Lagoa')),
        ('largo', _('Largo')),
        ('loteamento', _('Loteamento')),
        ('morro', _('Morro')),
        ('nucleo', _('Núcleo')),
        ('parque', _('Parque')),
        ('passarela', _('Passarela')),
        ('patio', _('Pátio')),
        ('praca', _('Praça')),
        ('quadra', _('Quadra')),
        ('recanto', _('Recanto')),
        ('residencial', _('Residencial')),
        ('rodovia', _('Rodovia')),
        ('rua', _('Rua')),
        ('setor', _('Setor')),
        ('sitio', _('Sítio')),
        ('travessa', _('Travessa')),
        ('trecho', _('Trecho')),
        ('trevo', _('Trevo')),
        ('vale', _('Vale')),
        ('vereda', _('Vereda')),
        ('via', _('Via')),
        ('viaduto', _('Viaduto')),
        ('viela', _('Viela')),
        ('vila', _('Vila')),
        ('outro', _('Outro')),
    )
    tipo = models.CharField(_('tipo'), max_length=15, choices=TIPO_CHOICES)
    logradouro = models.CharField(_('logradouro'), max_length=100)
    numero = models.CharField(_('número'), max_length=15, blank=True)
    complemento = models.CharField(_('complemento'), max_length=15, blank=True)
    referencia = models.CharField(_('referência'), max_length=100, blank=True)
    bairro = models.CharField(_('bairro'), max_length=100, blank=True)
    cep = models.CharField(
        _('CEP'),
        max_length=9,
        blank=True,
        null=True,
        help_text=_(u"formato: <em>XXXXX-XXX</em>.")
    )
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('município')
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')

    class Meta:
        ordering = ('logradouro', 'numero')
        verbose_name = _('endereço')
        verbose_name_plural = _('endereços')

    def __str__(self):
        return self.tipo + ' ' + self.logradouro + ', ' + self.numero \
            + ' ' + self.complemento + ' - ' + self.bairro
