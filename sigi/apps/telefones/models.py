# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Telefone(models.Model):
    TELEFONE_CHOICES = (
        ('F', 'Fixo'),
        ('M', 'Móvel'),
        ('X', 'Fax'),
    )
    codigo_ddd = models.CharField(
        'código DDD',
        max_length=2,
        help_text='Exemplo: <em>31</em>.'
    )
    numero = models.CharField(
        'número',
        max_length=9,
        help_text='Formato: <em>XXXX-XXXX</em>.'
    )
    tipo = models.CharField(
        max_length=1,
        choices=TELEFONE_CHOICES,
        radio_admin=True
    )
    nota = models.CharField(max_length=70, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('codigo_ddd', 'numero')
        unique_together = ('codigo_ddd', 'numero', 'tipo')

    class Admin:
        list_display = ('codigo_ddd', 'numero', 'tipo', 'nota')
        list_display_links = ('codigo_ddd', 'numero')
        list_filter = ('codigo_ddd',)
        search_fields = ('codigo_ddd', 'numero', 'tipo', 'nota')

    def __unicode__(self):
        return "(%s) %s" % (self.codigo_ddd, self.numero)
