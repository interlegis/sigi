# -*- coding: utf-8 -*-
from django.db import models
from sigi.apps.casas.models import CasaLegislativa

class Legislatura(models.Model):
    casa_legislativa = models.ForeignKey(CasaLegislativa)
    numero = models.PositiveSmallIntegerField(u'número legislatura')
    data_inicio = models.DateField(u'início')
    data_fim = models.DateField('fim')
    data_eleicao = models.DateField(u'data da eleição')
    total_parlamentares = models.PositiveIntegerField(u"Total de parlamentares")
    
    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True
    
    def meta(self):
        unique_together = (('casa_legislativa', 'numero'))
        ordering = ['casa_legislativa__municipio__uf__sigla', '-data_inicio']

    def __unicode__(self):
        return "%sª legislatura da %s (%s-%s)" % (self.numero, self.casa_legislativa.__unicode__(), self.data_inicio.year, self.data_fim.year)

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

    def __unicode__(self):
        return self.nome

class ComposicaoColigacao(models.Model):
    coligacao = models.ForeignKey(Coligacao, verbose_name='coligação')
    partido = models.ForeignKey('parlamentares.Partido')

    class Meta:
        verbose_name = 'composição da coligação'
        verbose_name_plural = 'composições das coligações'

    def __unicode__(self):
        return str(self.id)

class SessaoLegislativa(models.Model):
    SESSAO_CHOICES = (
        ('O', 'Ordinária'),
        ('E', 'Extraordinária'),
    )
    numero = models.PositiveSmallIntegerField(u'número da sessão', unique=True)
    mesa_diretora = models.ForeignKey(
        'MesaDiretora',
        verbose_name='Mesa Diretora'
    )
    legislatura = models.ForeignKey(Legislatura)
    tipo = models.CharField(
        max_length=1,
        choices=SESSAO_CHOICES,
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

    def __unicode__(self):
        return str(self.numero)

class MesaDiretora(models.Model):
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa'
   )

    class Meta:
        verbose_name = 'Mesa Diretora'
        verbose_name_plural = 'Mesas Diretoras'

    def __unicode__(self):
        return 'Mesa Diretora da %s' % unicode(self.casa_legislativa)

class Cargo(models.Model):
    descricao = models.CharField(u'descrição', max_length=30)

    class Meta:
        ordering = ('descricao',)

    def __unicode__(self):
        return self.descricao

class MembroMesaDiretora(models.Model):
    parlamentar = models.ForeignKey('parlamentares.Parlamentar')
    cargo = models.ForeignKey(Cargo)
    mesa_diretora = models.ForeignKey(MesaDiretora)

    class Meta:
        ordering = ('parlamentar',)
        unique_together = ('cargo', 'mesa_diretora')
        verbose_name = 'membro de Mesa Diretora'
        verbose_name_plural = 'membros de Mesas Diretora'

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.parlamentar), unicode(self.cargo))
