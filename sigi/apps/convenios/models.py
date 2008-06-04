# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.contrib.contenttypes import generic

class Convenio(models.Model):
    RECEBIDOS_CHOICES = (
        ('S', 'Sim'),
        ('N', 'Não'),
        ('P', 'Pendente'),
    )
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa'
    )
    num_convenio = models.PositiveIntegerField('número do convênio')
    num_processo_sf = models.CharField(
        'número do processo SF',
        max_length=11,
        help_text='Formato: <em>XXXXXX/XX-X</em>.'
    )
    data_adesao = models.DateField('data de adesão')
    data_retorno_assinatura = models.DateField(
        'data do retorno e assinatura',
        null=True,
        blank=True
    )
    data_termo_aceite = models.DateField(
        'data do Termo de Aceite',
        null=True,
        blank=True
    )
    data_publicacao = models.DateField(
        'data da publicação no Diário Oficial',
        null=True,
        blank=True
    )
    recebidos = models.CharField(
        'recebidos igual ao previsto?',
        max_length=1,
        choices=RECEBIDOS_CHOICES,
    )

    class Meta:
        get_latest_by = 'num_convenio'
        ordering = ('num_convenio',)
        verbose_name = 'convênio'

    class Admin:
        ordering = ('-num_convenio',)
        list_display = ('num_convenio', 'casa_legislativa',
                        'num_processo_sf', 'data_adesao')
        list_filter  = ('recebidos',)

class EquipamentoPrevisto(models.Model):
    convenio = models.ForeignKey(Convenio)
    equipamento = models.ForeignKey('inventario.Equipamento')
    quantidade = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'equipamento previsto'
        verbose_name_plural = 'equipamentos previstos'

    class Admin:
        ordering = ('convenio', 'equipamento')
        list_display = ('convenio', 'equipamento', 'quantidade')
        list_display_links = ('convenio', 'equipamento')

# class Ocorrencia(models.Model):
#     data_publicacao = models.DateField(
#         'data',
#         help_text='Data de publicação da ocorrência.'
#         default=datetime.now
#     )
#     ocorrencia = models.TextField('ocorrência')
#     convenio = models.ForeignKey(Convenio)
#
#     class Meta:
#         get_latest_by = 'data_publicacao'
#         ordering = ('-data_publicacao',)
#         verbose_name = 'ocorrência'
#
#     class Admin:
#         list_display = ('id', 'convenio', 'data_publicacao')
#
#     def __unicode__(self):
#         return self.id
