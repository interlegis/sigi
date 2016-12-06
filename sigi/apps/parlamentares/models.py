# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _

from sigi.apps.casas.models import CasaLegislativa


class Partido(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)

    class Meta:
        ordering = ('nome',)

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.nome), unicode(self.sigla))


class Parlamentar(models.Model):
    SEXO_CHOICES = (
        ('M', _(u'Masculino')),
        ('F', _(u'Feminino')),
    )
    nome_completo = models.CharField(max_length=128)
    nome_parlamentar = models.CharField(max_length=35, blank=True)
    foto = models.ImageField(
        upload_to='fotos/parlamentares',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True,
        null=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
    )
    data_nascimento = models.DateField(
        _(u'data de nascimento'),
        blank=True,
        null=True,
    )
    email = models.EmailField(_(u'e-mail'), blank=True)
    pagina_web = models.URLField(_(u'página web'),
                                 blank=True)

    class Meta:
        ordering = ('nome_completo',)
        verbose_name_plural = _(u'parlamentares')

    def __unicode__(self):
        if self.nome_parlamentar:
            return self.nome_parlamentar
        return self.nome_completo


class Mandato(models.Model):
    SUPLENCIA_CHOICES = (
        ('T', _(u'Titular')),
        ('S', _(u'Suplente')),
    )
    parlamentar = models.ForeignKey(Parlamentar)
    legislatura = models.ForeignKey('parlamentares.Legislatura')
    partido = models.ForeignKey(Partido)
    cargo = models.ForeignKey('parlamentares.Cargo')
    inicio_mandato = models.DateField(_(u'início de mandato'))
    fim_mandato = models.DateField(_(u'fim de mandato'))
    is_afastado = models.BooleanField(
        _(u'afastado'),
        default=False,
        help_text=_(u'Marque caso parlamentar não esteja ativo.')
    )

#    suplencia = models.CharField(
#        _(u'suplência'),
#        max_length=1,
#        choices=SUPLENCIA_CHOICES,
#    )

    def __unicode__(self):
        return str(self.id)


class Legislatura(models.Model):
    casa_legislativa = models.ForeignKey(CasaLegislativa)
    numero = models.PositiveSmallIntegerField(_(u'número legislatura'))
    data_inicio = models.DateField(_(u'início'))
    data_fim = models.DateField(_(u'fim'))
    data_eleicao = models.DateField(_(u'data da eleição'))
    total_parlamentares = models.PositiveIntegerField(_(u"Total de parlamentares"))

    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True

    class Meta:
        unique_together = (('casa_legislativa', 'numero'))
        ordering = ['casa_legislativa__municipio__uf__sigla', '-data_inicio']

    def __unicode__(self):
        return _(u"%(number)sª legislatura da %(parliament)s (%(initial_year)s-%(final_year)s)") % dict(
            number=self.numero,
            parliament=self.casa_legislativa.__unicode__(),
            initial_year=self.data_inicio.year,
            final_year=self.data_fim.year)


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
        verbose_name = _(u'coligação')
        verbose_name_plural = _(u'coligações')

    def __unicode__(self):
        return self.nome


class ComposicaoColigacao(models.Model):
    coligacao = models.ForeignKey(Coligacao, verbose_name=_(u'coligação'))
    partido = models.ForeignKey('parlamentares.Partido')

    class Meta:
        verbose_name = _(u'composição da coligação')
        verbose_name_plural = _(u'composições das coligações')

    def __unicode__(self):
        return str(self.id)


class SessaoLegislativa(models.Model):
    SESSAO_CHOICES = (
        ('O', _(u'Ordinária')),
        ('E', _(u'Extraordinária')),
    )
    numero = models.PositiveSmallIntegerField(_(u'número da sessão'), unique=True)
    mesa_diretora = models.ForeignKey(
        'MesaDiretora',
        verbose_name=_(u'Mesa Diretora')
    )
    legislatura = models.ForeignKey(Legislatura)
    tipo = models.CharField(
        max_length=1,
        choices=SESSAO_CHOICES,
        default='O'
    )
    data_inicio = models.DateField(_(u'início'))
    data_fim = models.DateField(_(u'fim'))
    data_inicio_intervalo = models.DateField(
        _(u'início de intervalo'),
        blank=True,
        null=True
    )
    data_fim_intervalo = models.DateField(
        _(u'fim de intervalo'),
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('legislatura', 'numero')
        verbose_name = _(u'Sessão Legislativa')
        verbose_name_plural = _(u'Sessões Legislativas')

    def __unicode__(self):
        return str(self.numero)


class MesaDiretora(models.Model):
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name=_(u'Casa Legislativa')
    )

    class Meta:
        verbose_name = _(u'Mesa Diretora')
        verbose_name_plural = _(u'Mesas Diretoras')

    def __unicode__(self):
        return _(u'Mesa Diretora da %s') % unicode(self.casa_legislativa)


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
        verbose_name = _(u'membro de Mesa Diretora')
        verbose_name_plural = _(u'membros de Mesa Diretora')

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.parlamentar), unicode(self.cargo))
