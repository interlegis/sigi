# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
#from django.contrib.contenttypes import ContentType
from django.contrib.contenttypes import generic
from sigi.apps.utils import SearchField

class Projeto(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
        
    def __unicode__(self):
        return self.sigla
    
class Convenio(models.Model):    
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa'
    )
    search_text = SearchField(field_names=['casa_legislativa'])
    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True
    projeto = models.ForeignKey(
        Projeto
    )
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
        'Aderidas',
        null=True,
        blank=True,
    )    
    data_retorno_assinatura = models.DateField(
        'Conveniadas',
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
        'Equipadas',
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
    data_devolucao_sem_assinatura = models.DateField(
        'data de devolução por falta de assinatura',
	null=True,
	blank=True,
	help_text=u'Data de devolução por falta de assinatura',
    )
    data_retorno_sem_assinatura = models.DateField(
	'data do retorno sem assinatura',
	null=True,
	blank=True,
	help_text=u'Data do retorno do convênio sem assinatura',
    )
    observacao = models.CharField(
        null=True, 
        blank=True,
        max_length=100,
    )
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
        return unicode(self.arquivo.name)
