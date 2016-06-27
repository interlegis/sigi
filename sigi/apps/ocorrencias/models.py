# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class Categoria(models.Model):
    nome = models.CharField(_(u"Categoria"), max_length=50)
    descricao = models.TextField(_(u'descrição'), blank=True, null=True)
    setor_responsavel = models.ForeignKey('servidores.Servico', verbose_name=_(u"Setor responsável"))

    class Meta:
        verbose_name, verbose_name_plural = _(u'Categoria'), _(u'Categorias')

    def __unicode__(self):
        return self.nome


class TipoContato(models.Model):
    descricao = models.CharField(_(u"Descrição"), max_length=50)

    class Meta:
        verbose_name, verbose_name_plural = _(u"Tipo de contato"), _(u"Tipos de contato")

    def __unicode__(self):
        return self.descricao


class Ocorrencia(models.Model):
    STATUS_ABERTO    = 1
    STATUS_REABERTO  = 2
    STATUS_RESOLVIDO = 3
    STATUS_FECHADO   = 4
    STATUS_DUPLICADO = 5
    
    STATUS_CHOICES = (
        (STATUS_ABERTO   , _(u'Aberto')),
        (STATUS_REABERTO , _(u'Reaberto')),
        (STATUS_RESOLVIDO, _(u'Resolvido')),
        (STATUS_FECHADO  , _(u'Fechado')),
        (STATUS_DUPLICADO, _(u'Duplicado')),
    )

    PRIORITY_CHOICES = (
        (1, _(u'Altíssimo')),
        (2, _(u'Alto')),
        (3, _(u'Normal')),
        (4, _(u'Baixo')),
        (5, _(u'Baixíssimo')),
    )

    casa_legislativa = models.ForeignKey('casas.CasaLegislativa', verbose_name=_(u'Casa Legislativa'))
    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True
    data_criacao = models.DateField(_(u'Data de criação'), null=True, blank=True, auto_now_add=True)
    data_modificacao = models.DateField(_(u'Data de modificação'), null=True, blank=True, auto_now=True)
    categoria = models.ForeignKey(Categoria, verbose_name=_(u'Categoria'))
    tipo_contato = models.ForeignKey(TipoContato, verbose_name=_(u"Tipo de contato"))
    assunto = models.CharField(_(u'Assunto'), max_length=200)
    assunto.grupo_filter = True
    status = models.IntegerField(_(u'Status'), choices=STATUS_CHOICES, default=1,)
    status.multichoice_filter = True
    prioridade = models.IntegerField(_(u'Prioridade'), choices=PRIORITY_CHOICES, default=3, )
    descricao = models.TextField(_(u'descrição'), blank=True,)
    resolucao = models.TextField(_(u'resolução'), blank=True,)
    servidor_registro = models.ForeignKey('servidores.Servidor', verbose_name=_(u"Servidor que registrou a ocorrência"))
    setor_responsavel = models.ForeignKey('servidores.Servico', verbose_name=_(u"Setor responsável"))
    ticket = models.PositiveIntegerField(_(u'Número do ticket'), blank=True, null=True, help_text=_(u"Número do ticket no osTicket"))

    class Meta:
        verbose_name, verbose_name_plural = _(u'ocorrência'), _(u'ocorrências')
        ordering = ['prioridade', 'data_modificacao', 'data_criacao', ]

    def __unicode__(self):
        return u"%(casa_legislativa)s: %(assunto)s" % {'assunto': self.assunto, 'casa_legislativa': self.casa_legislativa}

    def clean(self):
        if self.ticket is not None and Ocorrencia.objects.exclude(pk=self.pk).filter(ticket=self.ticket).exists():
            raise ValidationError({'ticket': _(u"Já existe ocorrência registrada para este ticket")})
        return super(Ocorrencia, self).clean()
    
    def get_ticket_url(self):
        return mark_safe(settings.OSTICKET_URL % self.ticket)

class Comentario(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, verbose_name=_(u'Ocorrência'), related_name='comentarios')
    data_criacao = models.DateTimeField(_(u'Data de criação'), null=True, blank=True, auto_now_add=True)
    descricao = models.TextField(_(u'Descrição'), blank=True, null=True)
    usuario = models.ForeignKey('servidores.Servidor', verbose_name=_(u'Usuário'))
    novo_status = models.IntegerField(_(u'Novo status'), choices=Ocorrencia.STATUS_CHOICES, blank=True, null=True)
    encaminhar_setor = models.ForeignKey('servidores.Servico', verbose_name=_(u'Encaminhar para setor'), blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.encaminhar_setor and (self.encaminhar_setor != self.ocorrencia.setor_responsavel):
            self.ocorrencia.setor_responsavel = self.encaminhar_setor
            self.ocorrencia.save()
        if self.novo_status and (self.novo_status != self.ocorrencia.status):
            self.ocorrencia.status = self.novo_status
            self.ocorrencia.save()
        super(Comentario, self).save(*args, **kwargs)


class Anexo(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, verbose_name=_(u'ocorrência'))
    arquivo = models.FileField(_(u'Arquivo anexado'), upload_to='apps/ocorrencia/anexo/arquivo', max_length=500)
    descricao = models.CharField(_(u'descrição do anexo'), max_length=70)
    data_pub = models.DateTimeField(_(u'data da publicação do anexo'), null=True, blank=True, auto_now_add=True)

    class Meta:
        ordering = ('-data_pub',)
        verbose_name, verbose_name_plural = _(u'Anexo'), _(u'Anexos')

    def __unicode__(self):
        return u"%(arquivo_name)s: %(descricao)s" % {'arquivo_name': self.arquivo.name, 'descricao': self.descricao}
