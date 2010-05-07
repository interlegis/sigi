# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
#from django.contrib.contenttypes import ContentType
from django.contrib.contenttypes import generic

class Convenio(models.Model):
    CONVENIO_TIPO = (
    ('PI', 'Programa Interlegis'),
    ('PPL', 'Projeto Piloto de Modernização'),
    ('PML', 'Projeto Modernização Legislaivo')
    )
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa'
    )
    num_processo_sf = models.CharField(
        'número do processo SF',
        max_length=11,
        blank=True,
        help_text='Formato: <em>XXXXXX/XX-X</em>.'
    )
    data_adesao = models.DateField(
        'data de adesão',
        null=True,
        blank=True,
    )
    tipo_convenio = models.CharField(
        max_length=10,
        choices=CONVENIO_TIPO
    )
    data_retorno_assinatura = models.DateField(
        'data do retorno e assinatura',
        null=True,
        blank=True,
        help_text='Convênio firmado.'
    )
    data_pub_diario = models.DateField(
        'data da publicação no Diário Oficial',
        null=True,
        blank=True
    )
    data_termo_aceite = models.DateField(
        'data do Termo de Aceite',
        null=True,
        blank=True,
        help_text='Equipamentos recebidos.'
    )
    data_devolucao_via = models.DateField(
        'data de devolução da via',
        null=True,
        blank=True,
        help_text='Data de devolução da via do convênio à Câmara Municipal.'
    )
    data_postagem_correio = models.DateField(
        'data postagem correio',
        null=True,
        blank=True,
    )
    #content_type = models.ForeignKey(ContentType)    

    class Meta:
        get_latest_by = 'id'
        ordering = ('id',)
        verbose_name = 'convênio'

    def __unicode__(self):
        return str(self.id)

class EquipamentoPrevisto(models.Model):
    convenio = models.ForeignKey(Convenio, verbose_name='convênio')
    equipamento = models.ForeignKey('inventario.Equipamento')
    quantidade = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'equipamento previsto'
        verbose_name_plural = 'equipamentos previstos'

    def __unicode__(self):
        return '%s %s(s)' % (self.quantidade, self.equipamento)

class Anexo(models.Model):
    convenio = models.ForeignKey(Convenio, verbose_name='convênio')
    arquivo = models.FileField(upload_to='apps/convenios/anexo/arquivo',)
    descricao = models.CharField('descrição', max_length='70')
    data_pub = models.DateTimeField(
        'data da publicação do anexo',
        default=datetime.now
    )

    class Meta:
        ordering = ('-data_pub',)

    def __unicode__(self):
        return self.arquivo.name
