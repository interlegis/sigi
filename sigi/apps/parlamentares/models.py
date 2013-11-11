# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic


class Partido(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)

    class Meta:
        ordering = ('nome',)

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.nome), unicode(self.sigla))


class Parlamentar(models.Model):
    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
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
        'data de nascimento',
        blank=True,
        null=True,
    )
    email = models.EmailField('e-mail', blank=True)
    pagina_web = models.URLField(u'página web',
                                 blank=True)

    class Meta:
        ordering = ('nome_completo',)
        verbose_name_plural = 'parlamentares'

    def __unicode__(self):
        if self.nome_parlamentar:
            return self.nome_parlamentar
        return self.nome_completo


class Mandato(models.Model):
    SUPLENCIA_CHOICES = (
        ('T', 'Titular'),
        ('S', 'Suplente'),
    )
    parlamentar = models.ForeignKey(Parlamentar)
    legislatura = models.ForeignKey('mesas.Legislatura')
    partido = models.ForeignKey(Partido)
    cargo = models.ForeignKey('mesas.Cargo')
    inicio_mandato = models.DateField(u'início de mandato')
    fim_mandato = models.DateField('fim de mandato')
    is_afastado = models.BooleanField(
        'afastado',
        default=False,
        help_text=u'Marque caso parlamentar não esteja ativo.'
    )

#    suplencia = models.CharField(
#        u'suplência',
#        max_length=1,
#        choices=SUPLENCIA_CHOICES,
#    )


    def __unicode__(self):
        return str(self.id)
