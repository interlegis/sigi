# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic
from apps.casas.models import CasaLegislativa
from datetime import date

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

class DominioLeg(models.Model):
    casa_legislativa = models.OneToOneField(CasaLegislativa)
    dominio = models.URLField('Domínio', verify_exists=False)
    contato_administrativo = models.CharField('Contato administrativo', max_length=60)
    telefone_administrativo = models.CharField('Telefone administrativo', max_length=10, help_text='Somente números: ddaaaannnn.')
    email_administrativo = models.EmailField('e-mail')
    contato_tecnico = models.CharField('Contato técnico', max_length=60)
    telefone_tecnico = models.CharField('Telefone administrativo', max_length=10, help_text='Somente números: ddaaaannnn.')
    email_tecnico = models.EmailField('e-mail')
    data_preenchimento = models.DateField('Data de preenchimento', default=date.today)
    data_recebimento = models.DateField('Data de recebimento', null=True, blank=True)
    data_atendimento = models.DateField('Data de atendimento', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Registro de domínio .leg.br'
        verbose_name_plural = 'Registros de domínios .leg.br'
        
    def __unicode__(self):
        return str(self.dominio)
    
    