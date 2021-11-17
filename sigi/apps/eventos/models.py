# -*- coding: utf-8 -*-
from datetime import datetime
import random
from django.db import models
from django.db.models import Sum
from django.utils.functional import lazy
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from sigi.apps.casas.models import Orgao
from sigi.apps.contatos.models import Municipio
from sigi.apps.servidores.models import Servidor
from django.core.exceptions import ValidationError

class TipoEvento(models.Model):
    CATEGORIA_CHOICES = (
        ('C', _(u'Curso')),
        ('E', _(u'Encontro')),
        ('O', _(u'Oficina')),
        ('S', _(u'Seminário')),
        ('V', _(u'Visita')),

    )
    nome = models.CharField(_(u"Nome"), max_length=100)
    categoria = models.CharField(
        _(u'Categoaria'),
        max_length=1,
        choices=CATEGORIA_CHOICES
    )
    class Meta:
        ordering = ("nome",)
        verbose_name, verbose_name_plural = _(u"Tipo de evento"), _(u"Tipos de evento")

    def __unicode__(self):
        return self.nome

class Evento(models.Model):
    STATUS_CHOICES = (
        ('P', _(u"Previsão")),
        ('A', _(u"A confirmar")),
        ('O', _(u"Confirmado")),
        ('R', _(u"Realizado")),
        ('C', _(u"Cancelado"))
    )

    tipo_evento = models.ForeignKey(
        TipoEvento,
        on_delete=models.PROTECT,
    )
    nome = models.CharField(_(u"Nome do evento"), max_length=100)
    descricao = models.TextField(_(u"Descrição do evento"))
    virtual = models.BooleanField(_("Virtual"), default=False)
    solicitante = models.CharField(_(u"Solicitante"), max_length=100)
    data_inicio = models.DateTimeField(
        _(u"Data/hora do Início"),
        null=True,
        blank=True
    )
    data_termino = models.DateTimeField(
        _(u"Data/hora do Termino"),
        null=True,
        blank=True
    )
    carga_horaria = models.PositiveIntegerField(
        _(u"carga horária"),
        default=0
    )
    casa_anfitria = models.ForeignKey(
        Orgao,
        on_delete=models.PROTECT,
        verbose_name=_(u"Casa anfitriã"),
        blank=True,
        null=True
    )
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT
    )
    local = models.TextField(_(u"Local do evento"), blank=True)
    publico_alvo = models.TextField(_(u"Público alvo"), blank=True)
    total_participantes = models.PositiveIntegerField(
        _(u"Total de participantes"),
        default=0,
        help_text=_(u"Se informar quantidade de participantes na aba de "
                    u"convites, este campo será ajustado com a somatória "
                    u"dos participantes naquela aba.")
    )
    status = models.CharField(_(u"Status"), max_length=1, choices=STATUS_CHOICES)
    data_cancelamento = models.DateField(_(u"Data de cancelamento"), blank=True, null=True)
    motivo_cancelamento = models.TextField(_(u"Motivo do cancelamento"), blank=True)

    class Meta:
        ordering = ("-data_inicio",)
        verbose_name, verbose_name_plural = _(u"Evento"), _(u"Eventos")

    def __unicode__(self):
        return _("%(nome)s (%(tipo_evento)s): de %(data_inicio)s a %(data_termino)s") % dict(
                    nome=self.nome,
                    tipo_evento=unicode(self.tipo_evento),
                    data_inicio=self.data_inicio,
                    data_termino=self.data_termino)

    def save(self, *args, **kwargs):
        if self.status != 'C':
            self.data_cancelamento = None
            self.motivo_cancelamento = ""
        if self.data_inicio > self.data_termino:
            raise ValidationError(_(u"Data de término deve ser posterior à "
                                    u"data de início"))
        total = self.convite_set.aggregate(total=Sum('qtde_participantes'))
        total = total['total']
        if (total is not None) or (total > 0):
            self.total_participantes = total
        return super(Evento, self).save(*args, **kwargs)

class Funcao(models.Model):
    nome = models.CharField(_(u"Função na equipe de evento"), max_length=100)
    descricao = models.TextField(_(u"Descrição da função"))

    class Meta:
        ordering = ("nome",)
        verbose_name, verbose_name_plural = _(u"Função"), _(u"Funções")

    def __unicode__(self):
        return self.nome

class Equipe(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE
    )
    membro = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        related_name="equipe_evento"
    )
    funcao = models.ForeignKey(
        Funcao,
        on_delete=models.PROTECT,
        verbose_name=_(u"Função na equipe")
    )
    observacoes = models.TextField(_(u"Observações"), blank=True)

    class Meta:
        ordering = ('evento', 'funcao', 'membro',)
        verbose_name, verbose_name_plural = _(u"Membro da equipe"), _(u"Membros da equipe")

    def __unicode__(self):
        return u"%s (%s)" % (unicode(self.membro), unicode(self.funcao),)

class Convite(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE
    )
    casa = models.ForeignKey(
        Orgao,
        on_delete=models.PROTECT,
        verbose_name=_(u"Casa convidada")
    )
    servidor = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        verbose_name=_(u"Servidor que convidou")
    )
    data_convite = models.DateField(_(u"Data do convite"))
    aceite = models.BooleanField(_("Aceitou o convite"), default=False)
    participou = models.BooleanField(_(u"Participou do evento"), default=False)
    qtde_participantes = models.PositiveIntegerField(
        _(u"número de participantes"),
        default=0
    )
    nomes_participantes = models.TextField(
        _(u"nome dos participantes"),
        blank=True,
        help_text=_(u"Favor colocar um participante por linha")
    )

    class Meta:
        ordering = ('evento', 'casa', '-data_convite')
        unique_together = ('evento', 'casa')
        verbose_name = _(u"Casa convidada")
        verbose_name_plural = _(u"Casas convidadas")

class Modulo(models.Model):
    TIPO_CHOICES = (
        ('A', _(u'Aula')),
        ('P', _(u'Palestra')),
        ('R', _(u'Apresentação')),
    )
    evento = models.ForeignKey(Evento, verbose_name=_(u"Evento"))
    nome = models.CharField(_(u"Nome"), max_length=100)
    descricao = models.TextField(_(u"Descrição do módulo"))
    tipo = models.CharField(_(u'Tipo'), max_length=1, choices=TIPO_CHOICES)
    inicio = models.DateTimeField(
        _(u"Data/hora de início"),
        null=True,
        blank=True
    )
    termino = models.DateTimeField(
        _(u"Data/hora de término"),
        null=True,
        blank=True
    )
    carga_horaria = models.PositiveIntegerField(
        _(u"carga horária"),
        default=0
    )
    apresentador = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        related_name="modulo_apresentador",
        null=True,
        blank=True,
        verbose_name=_(u"Apresentador"),
    )
    monitor = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        related_name="modulo_monitor",
        null=True,
        blank=True,
        verbose_name=_(u"Monitor"),
        help_text=_(u"Monitor, mediador, auxiliar, etc.")
    )
    qtde_participantes = models.PositiveIntegerField(
        _(u"número de participantes"),
        default=0,
        help_text=_(u"Deixar Zero significa que todos os participantes "
                    u"do evento participaram do módulo"),
    )

    class Meta:
        ordering = ('inicio',)
        verbose_name = _(u"Módulo do evento")
        verbose_name_plural = _(u"Módulos do evento")

    def __unicode__(self):
        return _(u"{nome} ({tipo})").format(
            nome=self.nome,
            tipo=self.get_tipo_display()
        )
