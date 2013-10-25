# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.contrib.contenttypes import generic
from sigi.apps.utils import SearchField


class Projeto(models.Model):
    """ Modelo para representar os projetos do programa
    Interlegis
    """
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)

    def __unicode__(self):
        return self.sigla


class Convenio(models.Model):
    """ Modelo que representa um convênio do Interlegis
    com uma Casa Legislativa.

    Uma Casa Legislativa pode não ter um convênio e sim 
    apenas uma adesão com o Interlegis, isto é,
    não tem compromissos direto com o Interlegis apenas
    um pacto de colaboração entre as partes
    """
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa'
    )
    # campo de busca em caixa baixa e sem acentos
    search_text = SearchField(field_names=['casa_legislativa'])
    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True
    projeto = models.ForeignKey('Projeto')
    # numero designado pelo Senado Federal para o convênio
    num_processo_sf = models.CharField(
        'número do processo SF (Senado Federal)',
        max_length=20,
        blank=True,
        help_text='Formatos:<br/>Antigo: <em>XXXXXX/XX-X</em>.<br/><em>SIGAD: XXXXX.XXXXXX/XXXX-XX</em>'
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
        if self.data_retorno_assinatura != None: 
            return u"Convênio nº %s - projeto %s, em %s" % (self.num_convenio, self.projeto.sigla, self.data_retorno_assinatura)
        else:
            return u"Adesão ao projeto %s, em %s" % (self.projeto.sigla, self.data_adesao)


class EquipamentoPrevisto(models.Model):
    """ Modelo utilizado para registrar os equipamentos
    disponibilizados para as Casas Legislativas
    (foi usado na prmeira etapa do programa)
    """
    convenio = models.ForeignKey(Convenio, verbose_name=u'convênio')
    equipamento = models.ForeignKey('inventario.Equipamento')
    quantidade = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'equipamento previsto'
        verbose_name_plural = 'equipamentos previstos'

    def __unicode__(self):
        return u'%s %s(s)' % (self.quantidade, self.equipamento)


class Anexo(models.Model):
    """ Modelo para giardar os documentos gerados
    no processo de convênio
    """
    convenio = models.ForeignKey(Convenio, verbose_name=u'convênio')
    # caminho no sistema para o documento anexo
    arquivo = models.FileField(upload_to='apps/convenios/anexo/arquivo',)
    descricao = models.CharField('descrição', max_length='70')
    data_pub = models.DateTimeField(
        'data da publicação do anexo',
        default=datetime.now
    )

    class Meta:
        ordering = ('-data_pub',)

    def __unicode__(self):
        return unicode("%s publicado em %s" % (self.descricao, self.data_pub))

class UnidadeAdministrativa(models.Model):
    """ Modelo para representar uma Unidade Administrativa
    que pode ser um servivo do próprio Interlegis, assim como
    uma unidade do Senado Federal
    """
    sigla = models.CharField(max_length='10')
    nome = models.CharField(max_length='100')

    def __unicode__(self):
        return unicode(self.sigla)


class Tramitacao(models.Model):
    """ Modelo para registrar as vias do processo de convênio e a Unidade
    responsável pelo tramite (ex. colher assinaturas do secretário do senado)
    """
    convenio = models.ForeignKey(Convenio, verbose_name=u'convênio')
    unid_admin = models.ForeignKey(UnidadeAdministrativa, verbose_name=u'Unidade Administrativa')
    data = models.DateField()
    observacao = models.CharField(
        'observação',
        max_length='512',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = u'Tramitações'

    def __unicode__(self):
        if self.observacao:
            return unicode("%s em %s (%s)" % (self.unid_admin, self.data, self.observacao))
        else:
            return unicode("%s em %s" % (self.unid_admin, self.data))

