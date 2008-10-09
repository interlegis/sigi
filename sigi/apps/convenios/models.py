# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.contrib.contenttypes import generic

class Convenio(models.Model):
    RECEBIDOS_CHOICES = (
        ('N', 'Não'),
        ('S', 'Sim'),
        ('P', 'Pendente(s)'),
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
    data_pub_diario = models.DateField(
        'data da publicação no Diário Oficial',
        null=True,
        blank=True
    )
    equipamentos_recebidos = models.CharField(
        max_length=1,
        choices=RECEBIDOS_CHOICES,
    )
    servicos = models.ManyToManyField(
        'servicos.Servico',
        verbose_name='serviços prestados',
        null=True,
        blank=True
    )

    class Meta:
        get_latest_by = 'num_convenio'
        ordering = ('num_convenio',)
        verbose_name = 'convênio'

    def __unicode__(self):
        return str(self.num_convenio)

class EquipamentoPrevisto(models.Model):
    convenio = models.ForeignKey(Convenio, verbose_name='convênio')
    equipamento = models.ForeignKey('inventario.Equipamento')
    quantidade = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'equipamento previsto'
        verbose_name_plural = 'equipamentos previstos'

    def __unicode__(self):
        return '%s %s(s)' % (self.quantidade, self.equipamento)

class Anexo(models.Model):
    convenio = models.ForeignKey(Convenio, verbose_name='convênio')
    arquivo = models.FileField(upload_to='apps/convenios/anexo/arquivo',)
    descricao = models.CharField('descrição', max_length='70')
    data_pub = models.DateTimeField(
        'data da publicação do anexo',
        default=datetime.now
    )

    class Meta:
        ordering = ('-data_pub',)

    def __unicode__(self):
        return self.arquivo.name
