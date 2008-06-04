# -*- coding: utf-8 -*-
from django.db import models

class Legislatura(models.Model):
    numero = models.PositiveSmallIntegerField(u'número legislatura')
    data_inicio = models.DateField(u'início')
    data_fim = models.DateField('fim')
    data_eleicao = models.DateField(u'data da eleição')

    class Admin:
        list_display = ('numero', 'data_inicio', 'data_fim', 'data_eleicao')
        list_display_links = ('numero',)

    def __unicode__(self):
        return str(self.numero)

class Coligacao(models.Model):
    nome = models.CharField(max_length=50)
    legislatura = models.ForeignKey(Legislatura)
    numero_votos = models.PositiveIntegerField(
        u'número de votos',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('legislatura', 'nome')
        verbose_name = 'coligação'
        verbose_name_plural = 'coligações'

    class Admin:
        list_display = ('nome', 'legislatura', 'numero_votos')
        list_display_links = ('nome',)
        search_fields = ('nome',)

    def __unicode__(self):
        return self.nome

class ComposicaoColigacao(models.Model):
    coligacao = models.ForeignKey(Coligacao)
    partido = models.ForeignKey('parlamentares.Partido')

    class Meta:
        verbose_name = 'composição da coligação'
        verbose_name_plural = 'composições das coligações'

    class Admin:
        list_display = ('coligacao', 'partido')
        list_display_links = ('coligacao', 'partido')
        list_filter = ('partido',)


class SessaoLegislativa(models.Model):
    SESSAO_CHOICES = (
        ('O', 'Ordinária'),
        ('E', 'Extraordinária'),
    )
    numero = models.PositiveSmallIntegerField(u'número da sessão', unique=True)
    legislatura = models.ForeignKey(Legislatura)
    tipo = models.CharField(
        max_length=1,
        choices=SESSAO_CHOICES,
        radio_admin=True,
        default='O'
    )
    data_inicio = models.DateField(u'início')
    data_fim    = models.DateField('fim')
    data_inicio_intervalo = models.DateField(
        u'início de intervalo',
        blank=True,
        null=True
    )
    data_fim_intervalo = models.DateField(
        'fim de intervalo',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('legislatura', 'numero')
        verbose_name = 'Sessão Legislativa'
        verbose_name_plural = 'Sessões Legislativas'

    class Admin:
        list_display = ('numero', 'legislatura', 'tipo', 'data_inicio', 'data_fim')
        list_display_links = ('numero',)
        list_filter = ('tipo',)

    def __unicode__(self):
        return self.numero

class MesaDiretora(models.Model):
    legislatura = models.ForeignKey(Legislatura)

    class Meta:
        verbose_name = 'Mesa Diretora'
        verbose_name_plural = 'Mesas Diretoras'

    class Admin:
        list_display = ('legislatura',)

    def __unicode__(self):
        return self.legislatura

class Cargo(models.Model):
    descricao = models.CharField(u'descrição', max_length=30)

    class Meta:
        ordering = ('descricao',)

    class Admin:
        list_display = ('descricao',)

    def __unicode__(self):
        return self.descricao

class MembroMesaDiretora(models.Model):
    parlamentar = models.ForeignKey(
        'parlamentares.Parlamentar',
        core=True,
    )
    cargo = models.ForeignKey(Cargo, core=True)
    mesa_diretora = models.ForeignKey(
        MesaDiretora,
        edit_inline=True,
        max_num_in_admin=11,
        num_extra_on_change=4,
        num_in_admin=4
    )

    class Meta:
        ordering = ('parlamentar',)
        verbose_name = 'membro de Mesa Diretora'
        verbose_name_plural = 'membros de Mesas Diretora'

    class Admin:
        list_display = ('parlamentar', 'cargo')
        list_display_links = ('parlamentar', 'cargo')
        list_filter = ('cargo',)
        search_fields = ('parlamentar', 'cargo')

    def __unicode__(self):
        return '%s (%s)' % (self.parlamentar, self.cargo)
