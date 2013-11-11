# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.db import models
from sigi.apps.utils import SearchField
#from eav.models import BaseChoice, BaseEntity, BaseSchema, BaseAttribute


class Categoria(models.Model):
    nome= models.CharField(u"Nome Categoria", max_length=50)
    descricao = models.TextField(u'descrição', blank=True, null=True)
    setor_responsavel = models.ForeignKey('servidores.Servico', verbose_name=u"Setor responsável")
    
    class Meta:
        verbose_name, verbose_name_plural = u'Categoria', u'Categorias' 

    def __unicode__(self):
        return self.nome
  

class TipoContato(models.Model):
    descricao = models.CharField(u"Descrição", max_length=50)
    
    class Meta:
        verbose_name, verbose_name_plural = u"Tipo de contato", u"Tipos de contato"
        
    def __unicode__(self):
        return self.descricao


class Ocorrencia(models.Model):
    STATUS_CHOICES = (
        (1, u'Aberto'),
        (2, u'Reaberto'),
        (3, u'Resolvido'),
        (4, u'Fechado'),
        (5, u'Duplicado'),
    )

    PRIORITY_CHOICES = (
        (1, u'Altíssimo'),
        (2, u'Alto'),
        (3, u'Normal'),
        (4, u'Baixo'),
        (5, u'Baixíssimo'),
    )

    casa_legislativa = models.ForeignKey('casas.CasaLegislativa', verbose_name=u'Casa Legislativa')
    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True
    data_criacao = models.DateField(u'Data de criação', null=True, blank=True, auto_now_add=True)
    data_modificacao = models.DateField(u'Data de modificação', null=True, blank=True, auto_now=True)
    categoria = models.ForeignKey(Categoria, verbose_name=u'Categoria')
    tipo_contato = models.ForeignKey(TipoContato, verbose_name=u"Tipo de contato")
    assunto = models.CharField(u'Assunto', max_length=200)
    assunto.grupo_filter = True
    status = models.IntegerField(u'Status', choices=STATUS_CHOICES, default=1,)
    status.multichoice_filter = True
    prioridade = models.IntegerField(u'Prioridade', choices=PRIORITY_CHOICES, default=3, )
    descricao = models.TextField(u'descrição', blank=True,)
    resolucao = models.TextField(u'resolução', blank=True,)
    servidor_registro = models.ForeignKey('servidores.Servidor', verbose_name=u"Servidor que registrou a ocorrência")
    setor_responsavel = models.ForeignKey('servidores.Servico', verbose_name=u"Setor responsável")

    class Meta:
        verbose_name, verbose_name_plural = u'ocorrência', u'ocorrências'
        ordering = ['prioridade', 'data_modificacao', 'data_criacao', ]
        
    def __unicode__(self):
        return u"%(casa_legislativa)s: %(assunto)s" % {'assunto': self.assunto, 'casa_legislativa': self.casa_legislativa}


class Comentario(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, verbose_name=u'Ocorrência')
    data_criacao = models.DateTimeField(u'Data de criação', null=True, blank=True, auto_now_add=True)
    descricao = models.TextField(u'Descrição', blank=True, null=True)
    usuario = models.ForeignKey('servidores.Servidor', verbose_name=u'Usuário')
    novo_status = models.IntegerField(u'Novo status', choices=Ocorrencia.STATUS_CHOICES, blank=True, null=True)
    encaminhar_setor = models.ForeignKey('servidores.Servico', verbose_name=u'Encaminhar para setor', blank=True, null=True)


class Anexo(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, verbose_name=u'ocorrência')
    arquivo = models.FileField(u'Arquivo anexado', upload_to='apps/ocorrencia/anexo/arquivo',)
    descricao = models.CharField(u'descrição do anexo', max_length='70')
    data_pub = models.DateTimeField( u'data da publicação do anexo', null=True, blank=True, auto_now_add=True)

    class Meta:
        ordering = ('-data_pub',)
        verbose_name, verbose_name_plural = u'Anexo', u'Anexos' 

    def __unicode__(self):
        return u"%(arquivo_name)s: %(descricao)s" % {'arquivo_name': self.arquivo.name, 'descricao': self.descricao}
