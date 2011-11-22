# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.db import models
from sigi.apps.utils import SearchField
from eav.models import BaseChoice, BaseEntity, BaseSchema, BaseAttribute

class Categoria(models.Model):
    nome= models.CharField(max_length=50)
    descricao = models.TextField('descrição', blank=True, null=True)

    def __unicode__(self):
        return str(self.nome)

class Ocorrencia(models.Model):
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa'
    )
    search_text = SearchField(field_names=['casa_legislativa'])
    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True
    data_criacao = models.DateField(
        'data de criacao',
        null=True,
        blank=True,
    )

    data_modificacao = models.DateField(
        u'data de modificação',
        null=True,
        blank=True,
    )


    STATUS_CHOICES = (
        (1, 'Aberto'),
        (2, 'Reaberto'),
        (3, 'Resolvido'),
        (4, 'Fechado'),
        (5, 'Duplicado'),
    )

    PRIORITY_CHOICES = (
        (1, u'Altíssimo'),
        (2, 'Alto'),
        (3, 'Normal'),
        (4, 'Baixo'),
        (5, u'Baixíssimo'),
    )

    categoria = models.ForeignKey(Categoria)
    assunto = models.CharField(max_length=200)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, blank=1)
    prioridade = models.IntegerField(choices=PRIORITY_CHOICES, default=3, blank=3)
    descricao = models.TextField(u'descirção', blank=True, null=True)
    resolucao = models.TextField(u'resolução', blank=True, null=True)
    responsavel = models.ForeignKey('servidores.Servidor', blank=True, null=True, verbose_name=u'responsável')

    class Meta:
        verbose_name, verbose_name_plural = u'ocorrência', u'ocorrências'

class Comentario(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, verbose_name=u'ocorrência')
    data_criacao = models.DateTimeField(u'data de criação', default = datetime.now())
    descricao = models.TextField(u'descirção', blank=True, null=True)
    usuario = models.ForeignKey('servidores.Servidor', blank=True, null=True, verbose_name=u'usuário')

class Anexo(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, verbose_name=u'ocorrência')
    arquivo = models.FileField(upload_to='apps/ocorrencia/anexo/arquivo',)
    descricao = models.CharField('descrição', max_length='70')
    data_pub = models.DateTimeField(
        'data da publicação do anexo',
        default=datetime.now
    )

    class Meta:
        ordering = ('-data_pub',)

    def __unicode__(self):
        return unicode(self.arquivo.name)

