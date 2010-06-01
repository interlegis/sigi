# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
#from django.contrib.contenttypes import ContentType
from django.contrib.contenttypes import generic

class Projeto(models.Model):
    nome = models.CharField(max_length=50)
        
    def __unicode__(self):
        return self.nome
    
class Convenio(models.Model):    
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa'
    )
    casa_legislativa.uf_filter = True
    num_processo_sf = models.CharField(
        'número do processo SF',
        max_length=11,
        blank=True,
        help_text='Formato: <em>XXXXXX/XX-X</em>.'
    )
    num_convenio = models.CharField(
        'número do convênio',
        max_length=10,
        blank=True
    )
    data_adesao = models.DateField(
        'data de adesão',
        null=True,
        blank=True,
    )
    projeto = models.ForeignKey(
        Projeto
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
        help_text=u'Data de devolução da via do convênio à Câmara Municipal.'
    )
    data_postagem_correio = models.DateField(
        'data postagem correio',
        null=True,
        blank=True,
    )
    observacao = models.TextField(null=True, blank=True)
    conveniada = models.BooleanField()
    equipada = models.BooleanField()

    def save(self, *args, **kwargs):
        self.conveniada = self.data_retorno_assinatura!=None
        self.equipada = self.data_termo_aceite!=None
        super(Convenio, self).save(*args, **kwargs)


    class Meta:
        get_latest_by = 'id'
        ordering = ('id',)
        verbose_name = u'convênio'

    def __unicode__(self):
        return str(self.id)

class EquipamentoPrevisto(models.Model):
    convenio = models.ForeignKey(Convenio, verbose_name=u'convênio')
    equipamento = models.ForeignKey('inventario.Equipamento')
    quantidade = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'equipamento previsto'
        verbose_name_plural = 'equipamentos previstos'

    def __unicode__(self):
        return '%s %s(s)' % (self.quantidade, self.equipamento)

class Anexo(models.Model):
    convenio = models.ForeignKey(Convenio, verbose_name=u'convênio')
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
