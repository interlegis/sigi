# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic

class Servico(models.Model):
    SITUACAO_CHOICES = (
        ('P', 'Pendente'),
        ('A', 'Em andamento'),
        ('E', 'Executado'),
        ('D', 'Demanda'),
        ('C', 'Cancelado'),
    )
    AVALIACAO_CHOICES = (
        (4, 'Ótimo'),
        (3, 'Bom'),
        (2, 'Regular'),
        (1, 'Ruim'),
    )
    titulo = models.CharField('título', max_length=60)
    tipo = models.CharField(max_length=30)
    descricao = models.TextField(u'descrição')
    convenio = models.ForeignKey('convenios.Convenio', verbose_name='Convênio')
    colaboradores = generic.GenericRelation('contatos.Contato')
    data_inicio = models.DateField(
        u'início',
        blank=True,
        null=True,
        help_text = 'Início da realização do serviço.',
    )
    data_fim = models.DateField(
        'fim',
        blank=True,
        null=True,
        help_text = 'Fim da realização do serviço.',
    )
    situacao = models.CharField(
        u'situação',
        max_length=1,
        choices=SITUACAO_CHOICES
    )
    avaliacao = models.PositiveSmallIntegerField(
        u'avaliação',
        choices=AVALIACAO_CHOICES,
        blank=True,
        null=True,
        help_text='Avaliação que o serviço obteve, quando aplicável.'
    )

    class Meta:
        verbose_name = 'serviço'
        verbose_name_plural = 'serviços'

    def __unicode__(self):
        return str(self.titulo)
