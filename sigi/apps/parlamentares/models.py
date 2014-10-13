# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _


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
        blank=True
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
    legislatura = models.ForeignKey('mesas.Legislatura')
    partido = models.ForeignKey(Partido)
    cargo = models.ForeignKey('mesas.Cargo')
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
