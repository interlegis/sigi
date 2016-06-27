# -*- coding: utf-8 -*-
from __future__ import absolute_import

import base64

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from sigi.apps.crud.utils import UF, YES_NO_CHOICES
from sigi.apps.utils import SearchField


class Subsecretaria(models.Model):

    nome = models.CharField(verbose_name=_(u'Nome'), max_length=100, null=True)
    sigla = models.CharField(verbose_name=_(u'Sigla'),
                             max_length=10, null=True)

    class Meta(object):
        ordering = (u'nome', u'sigla')
        verbose_name = _(u'Subsecretaria')
        verbose_name_plural = _(u'Subsecretarias')

    def __str__(self):
        return u'[%s] %s' % (self.sigla, self.nome)


class Telefone(models.Model):
    TIPO_TELEFONE = [(u'FIXO', u'FIXO'), (u'CELULAR', u'CELULAR')]

    tipo = models.CharField(
        max_length=7,
        choices=TIPO_TELEFONE,
        verbose_name=_(u'Tipo Telefone'),)
    ddd = models.CharField(max_length=2, verbose_name=_(u'DDD'))
    numero = models.CharField(max_length=10, verbose_name=_(u'Número'))
    principal = models.CharField(
        max_length=10,
        verbose_name=_(u'Telefone Principal?'),
        choices=YES_NO_CHOICES)

    class Meta(object):
        verbose_name = _(u'Telefone')
        verbose_name_plural = _(u'Telefones')

    def __str__(self):
        return u'(%s) %s' % (self.ddd, self.numero)


class ConfirmaEmail(models.Model):
    u"""
        Classe de email
    """
    email = models.EmailField(unique=True, verbose_name=_(u'Email'))
    confirmado = models.BooleanField(default=False)
    token = models.CharField(
        max_length=50, verbose_name=_(u'Hash do Email'))
    user_id = models.TextField(blank=True, verbose_name=_(u'ID do Usuário'))

    class Meta(object):
        verbose_name = _(u'Email')
        verbose_name_plural = _(u'Emails')


class Usuario(models.Model):
    u'''
        Usuário cadastrado via web
    '''

    TIPO_VINCULO = [(u'Tercerizado', u'Tercerizado'),
                    (u'Efetivo', u'Efetivo'),
                    (u'Contratado', u'Contratado')]

    user = models.ForeignKey(User)
    username = models.CharField(
        verbose_name=_(u'Nome de Usuário'),
        unique=True,
        max_length=50)
    nome_completo = models.CharField(
        verbose_name=_(u'Nome Completo'),
        max_length=128)
    data_criacao = models.DateTimeField(
        _(u'Data Criação'),
        default=timezone.now)
    data_ultima_atualizacao = models.DateTimeField(
        default=timezone.now, verbose_name=_(u'Última atualização'))
    email = email = models.EmailField(unique=True, verbose_name=_(u'Email'))
    email_confirmado = models.BooleanField(
        default=False, verbose_name=_(u'Email confirmado?'))
    habilitado = models.BooleanField(
        default=False,
        verbose_name=_(u'Habilitado?'))
    conveniado = models.BooleanField(default=False)
    responsavel = models.BooleanField(default=False)
    rg = models.CharField(
        max_length=9,
        null=True,
        verbose_name=_(u'RG'))
    cpf = models.CharField(
        max_length=11,
        verbose_name=_(u'CPF'),
        default=u'00000000000')
    cargo = models.CharField(
        max_length=30,
        verbose_name=_(u'Cargo'),
        default=u'--------')
    vinculo = models.CharField(
        max_length=30,
        verbose_name=_(u'Vinculo'),
        choices=TIPO_VINCULO,
        default=u'--------')
    primeiro_telefone = models.ForeignKey(
        Telefone, null=True, related_name=u'primeiro_telefone')
    segundo_telefone = models.ForeignKey(
        Telefone, null=True, related_name=u'segundo_telefone')

    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name=_(u'Casa Legislativa')
    )
    # campo de busca em caixa baixa e sem acentos
    search_text = SearchField(field_names=['casa_legislativa'])

    class Meta(object):
        verbose_name = _(u'Usuário')
        verbose_name_plural = _(u'Usuários')

    def __str__(self):
        return self.username
