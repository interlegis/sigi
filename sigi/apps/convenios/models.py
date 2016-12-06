# style="list-style-type: noneo -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext as _

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
        verbose_name=_(u'Casa Legislativa')
    )
    # campo de busca em caixa baixa e sem acentos
    search_text = SearchField(field_names=['casa_legislativa'])
    projeto = models.ForeignKey(_(u'Projeto'))
    # numero designado pelo Senado Federal para o convênio
    num_processo_sf = models.CharField(
        _(u'número do processo SF (Senado Federal)'),
        max_length=20,
        blank=True,
        help_text=_(u'Formatos:<br/>Antigo: <em>XXXXXX/XX-X</em>.<br/><em>SIGAD: XXXXX.XXXXXX/XXXX-XX</em>')
    )
    num_convenio = models.CharField(
        _(u'número do convênio'),
        max_length=10,
        blank=True
    )
    data_adesao = models.DateField(
        _(u'Aderidas'),
        null=True,
        blank=True,
    )
    data_retorno_assinatura = models.DateField(
        _(u'Conveniadas'),
        null=True,
        blank=True,
        help_text=_(u'Convênio firmado.')
    )
    data_pub_diario = models.DateField(
        _(u'data da publicação no Diário Oficial'),
        null=True,
        blank=True
    )
    data_termo_aceite = models.DateField(
        _(u'Equipadas'),
        null=True,
        blank=True,
        help_text=_(u'Equipamentos recebidos.')
    )
    data_devolucao_via = models.DateField(
        _(u'data de devolução da via'),
        null=True,
        blank=True,
        help_text=_(u'Data de devolução da via do convênio à Câmara Municipal.')
    )
    data_postagem_correio = models.DateField(
        _(u'data postagem correio'),
        null=True,
        blank=True,
    )
    data_devolucao_sem_assinatura = models.DateField(
        _(u'data de devolução por falta de assinatura'),
        null=True,
        blank=True,
        help_text=_(u'Data de devolução por falta de assinatura'),
    )
    data_retorno_sem_assinatura = models.DateField(
        _(u'data do retorno sem assinatura'),
        null=True,
        blank=True,
        help_text=_(u'Data do retorno do convênio sem assinatura'),
    )
    observacao = models.CharField(
        null=True,
        blank=True,
        max_length=100,
    )
    conveniada = models.BooleanField(default=False)
    equipada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.conveniada = self.data_retorno_assinatura is not None
        self.equipada = self.data_termo_aceite is not None
        super(Convenio, self).save(*args, **kwargs)

    class Meta:
        get_latest_by = 'id'
        ordering = ('id',)
        verbose_name = _(u'convênio')

    def __unicode__(self):
        if self.data_retorno_assinatura is not None:
            return _(u"Convênio nº %(number)s - projeto %(project)s, em %(date)s") % dict(
                number=self.num_convenio,
                project=self.projeto.sigla,
                date=self.data_retorno_assinatura)
        else:
            return _(u"Adesão ao projeto %(project)s, em %(date)s") % dict(
                project=self.projeto.sigla,
                date=self.data_adesao)


class EquipamentoPrevisto(models.Model):

    """ Modelo utilizado para registrar os equipamentos
    disponibilizados para as Casas Legislativas
    (foi usado na prmeira etapa do programa)
    """
    convenio = models.ForeignKey(Convenio, verbose_name=_(u'convênio'))
    equipamento = models.ForeignKey('inventario.Equipamento')
    quantidade = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = _(u'equipamento previsto')
        verbose_name_plural = _(u'equipamentos previstos')

    def __unicode__(self):
        return u'%s %s(s)' % (self.quantidade, self.equipamento)


class Anexo(models.Model):

    """ Modelo para giardar os documentos gerados
    no processo de convênio
    """
    convenio = models.ForeignKey(Convenio, verbose_name=_(u'convênio'))
    # caminho no sistema para o documento anexo
    arquivo = models.FileField(upload_to='apps/convenios/anexo/arquivo', max_length=500)
    descricao = models.CharField(_(u'descrição'), max_length=70)
    data_pub = models.DateTimeField(
        _(u'data da publicação do anexo'),
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
    sigla = models.CharField(max_length=10)
    nome = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.sigla)


class Tramitacao(models.Model):

    """ Modelo para registrar as vias do processo de convênio e a Unidade
    responsável pelo tramite (ex. colher assinaturas do secretário do senado)
    """
    convenio = models.ForeignKey(Convenio, verbose_name=_(u'convênio'))
    unid_admin = models.ForeignKey(UnidadeAdministrativa, verbose_name=_(u'Unidade Administrativa'))
    data = models.DateField()
    observacao = models.CharField(
        _(u'observação'),
        max_length=512,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = _(u'Tramitações')

    def __unicode__(self):
        in_date = _(u"em %(date)s") % dict(date=self.data)  # for focused translation
        result = u"%s %s" % (self.unid_admin, in_date)
        if self.observacao:
            result = result + u" (%s)" % (self.observacao)
        return unicode(result)  # XXX is this unicode(...) really necessary???
