# coding: utf-8
from django.db import models
from django.utils.translation import ugettext as _

from sigi.apps.casas.models import CasaLegislativa


class Legislatura(models.Model):
    casa_legislativa = models.ForeignKey(CasaLegislativa)
    numero = models.PositiveSmallIntegerField(_(u'número legislatura'))
    data_inicio = models.DateField(_(u'início'))
    data_fim = models.DateField(_(u'fim'))
    data_eleicao = models.DateField(_(u'data da eleição'))
    total_parlamentares = models.PositiveIntegerField(_(u"Total de parlamentares"))

    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True

    def meta(self):
        unique_together = (('casa_legislativa', 'numero'))
        ordering = ['casa_legislativa__municipio__uf__sigla', '-data_inicio']

    def __unicode__(self):
        return _(u"%sª legislatura da %s (%s-%s)") % (self.numero, self.casa_legislativa.__unicode__(), self.data_inicio.year, self.data_fim.year)


class Coligacao(models.Model):
    nome = models.CharField(max_length=50)
    legislatura = models.ForeignKey(Legislatura)
    numero_votos = models.PositiveIntegerField(
        _(u'número de votos'),
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('legislatura', 'nome')
        verbose_name = _('coligação')
        verbose_name_plural = _('coligações')

    def __unicode__(self):
        return self.nome


class ComposicaoColigacao(models.Model):
    coligacao = models.ForeignKey(Coligacao, verbose_name=_('coligação'))
    partido = models.ForeignKey('parlamentares.Partido')

    class Meta:
        verbose_name = _('composição da coligação')
        verbose_name_plural = _('composições das coligações')

    def __unicode__(self):
        return str(self.id)


class SessaoLegislativa(models.Model):
    SESSAO_CHOICES = (
        ('O', _('Ordinária')),
        ('E', _('Extraordinária')),
    )
    numero = models.PositiveSmallIntegerField(_(u'número da sessão'), unique=True)
    mesa_diretora = models.ForeignKey(
        'MesaDiretora',
        verbose_name=_('Mesa Diretora')
    )
    legislatura = models.ForeignKey(Legislatura)
    tipo = models.CharField(
        max_length=1,
        choices=SESSAO_CHOICES,
        default='O'
    )
    data_inicio = models.DateField(_(u'início'))
    data_fim = models.DateField(_('fim'))
    data_inicio_intervalo = models.DateField(
        _(u'início de intervalo'),
        blank=True,
        null=True
    )
    data_fim_intervalo = models.DateField(
        _('fim de intervalo'),
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('legislatura', 'numero')
        verbose_name = _('Sessão Legislativa')
        verbose_name_plural = _('Sessões Legislativas')

    def __unicode__(self):
        return str(self.numero)


class MesaDiretora(models.Model):
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name=_('Casa Legislativa')
    )

    class Meta:
        verbose_name = _('Mesa Diretora')
        verbose_name_plural = _('Mesas Diretoras')

    def __unicode__(self):
        return _('Mesa Diretora da %s') % unicode(self.casa_legislativa)


class Cargo(models.Model):
    descricao = models.CharField(_(u'descrição'), max_length=30)

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
        verbose_name = _('membro de Mesa Diretora')
        verbose_name_plural = _('membros de Mesas Diretora')

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.parlamentar), unicode(self.cargo))
