# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _

from sigi.apps.servicos.models import TipoServico
from sigi.apps.usuarios.models import Usuario


class Solicitacao(models.Model):
    usuario = models.ForeignKey(Usuario)
    sistema = models.ForeignKey(TipoServico)
    titulo = models.CharField(verbose_name=_(u'Título'), max_length=100)
    resumo = models.CharField(verbose_name=_(u'Resumo'), max_length=50)
    casa_legislativa = models.CharField(verbose_name=_(u'Casa Legislativa'),
                                        max_length=200)
    email_contato = models.EmailField(blank=True,
                                      null=True,
                                      verbose_name=_(u'Email de contato'))
    # Substituir por usuarios.models.Telefone?
    telefone_contato = models.CharField(max_length=15,
                                        null=True,
                                        blank=True,
                                        verbose_name=_(u'Telefone de contato'))

    data_criacao = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_(u'Data de criação'))
    descricao = models.TextField(blank=True,
                                 null=True,
                                 verbose_name=_(u'Descrição'))

    osticket = models.CharField(blank=True,
                                null=True,
                                max_length=256,
                                verbose_name=_(u'Código Ticket'))

    class Meta(object):
        verbose_name = _(u'Solicitação de Novo Serviço')
        verbose_name_plural = _(u'Solicitações de Novos Serviços')
        ordering = [u'data_criacao']

    def __str__(self):
        return u"%s - %s" % (self.codigo, self.resumo)
