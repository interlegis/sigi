#-*- coding: utf-8 -*-
import re
from datetime import datetime, date
from django.db import models
from django.utils.translation import ugettext as _
from sigi.apps.utils import SearchField
from sigi.apps.servidores.models import Servidor, Servico

class Projeto(models.Model):
    """ Modelo para representar os projetos do programa
    Interlegis
    """
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)

    def __unicode__(self):
        return self.sigla

class StatusConvenio(models.Model):
    nome = models.CharField(max_length=100)
    cancela = models.BooleanField(_(u"Cancela o convênio"), default=False)

    class Meta:
        ordering = ('nome',)
        verbose_name = _(u"Estado de convenios")
        verbose_name_plural = _(u"Estados de convenios")

    def __unicode__(self):
        return self.nome

class TipoSolicitacao(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ('nome',)
        verbose_name = _(u"tipo de solicitação")
        verbose_name_plural = _(u"Tipos de solicitação")

    def __unicode__(self):
        return self.nome

class Convenio(models.Model):
    casa_legislativa = models.ForeignKey(
        'casas.Orgao',
        on_delete=models.PROTECT,
        verbose_name=_(u'órgão conveniado')
    )
    # campo de busca em caixa baixa e sem acentos
    search_text = SearchField(field_names=['casa_legislativa'])
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.PROTECT,
    )
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
    data_sigi = models.DateField(
        _(u"data de cadastro no SIGI"),
        blank=True,
        null=True,
        auto_now_add=True
    )
    data_sigad = models.DateField(
        _(u"data de cadastro no SIGAD"),
        null=True,
        blank=True
    )
    data_solicitacao = models.DateField(
        _(u"data do e-mail de solicitação"),
        null=True,
        blank=True
    )
    tipo_solicitacao = models.ForeignKey(
        TipoSolicitacao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_(u"tipo de solicitação")
    )
    status = models.ForeignKey(
        StatusConvenio,
        on_delete=models.SET_NULL,
        verbose_name=_(u"estado atual"),
        null=True,
        blank=True
    )
    acompanha = models.ForeignKey(
        Servidor,
        on_delete=models.SET_NULL,
        related_name='convenios_acompanhados',
        verbose_name=_(u"acompanhado por"),
        null=True,
        blank=True
    )
    observacao = models.TextField(
        _(u"observações"),
        null=True,
        blank=True,
    )
    servico_gestao = models.ForeignKey(
        Servico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='convenios_geridos',
        verbose_name=_(u"serviço de gestão")
    )
    servidor_gestao = models.ForeignKey(
        Servidor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_(u"servidor de gestão")
    )
    data_adesao = models.DateField(
        _(u'aderidas'),
        null=True,
        blank=True,
    )
    data_retorno_assinatura = models.DateField(
        _(u'conveniadas'),
        null=True,
        blank=True,
        help_text=_(u'Convênio firmado.')
    )
    duracao = models.PositiveIntegerField(
        _(u"duração (meses)"),
        null=True,
        blank=True,
        help_text=_(u"Deixar em branco caso a duração seja indefinida")
        )
    data_pub_diario = models.DateField(
        _(u'data da publicação no Diário Oficial'),
        null=True,
        blank=True
    )
    data_termo_aceite = models.DateField(
        _(u'equipadas'),
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
    conveniada = models.BooleanField(default=False)
    equipada = models.BooleanField(default=False)

    def get_termino_convenio(self):
        if (self.data_retorno_assinatura is None or
            self.duracao is None):
            return None

        ano = self.data_retorno_assinatura.year + int(self.duracao / 12)
        mes = int(self.data_retorno_assinatura.month + int(self.duracao % 12))
        if mes > 12:
            ano = ano + 1
            mes = mes - 12
        dia = self.data_retorno_assinatura.day

        while True:
            try:
                data_fim = date(year=ano, month=mes,day=dia)
                break
            except:
                dia = dia - 1

        return data_fim

    def get_status(self):
        if self.status and self.status.cancela:
            return _(u"Cancelado")

        if self.data_retorno_assinatura is not None:
            if self.duracao is not None:
                if date.today() >= self.get_termino_convenio():
                    return _(u"Vencido")
            return _(u"Vigente")

        if (self.data_retorno_assinatura is None and
            self.data_devolucao_sem_assinatura is None and
            self.data_retorno_sem_assinatura is None):
            return _(u"Pendente")
        if (self.data_devolucao_sem_assinatura is not None or
            self.data_retorno_sem_assinatura is not None):
            return _(u"Desistência")

        return _(u"Indefinido")

    def get_sigad_url(self):
        m = re.match(
            r'(?P<orgao>00100|00200)\.(?P<sequencial>\d{6})/(?P<ano>\d{4})-\d{2}',
            self.num_processo_sf
        )
        if m:
            return (r'<a href="https://intra.senado.leg.br/'
                    r'sigad/novo/protocolo/impressao.asp?area=processo'
                    r'&txt_numero_orgao={orgao}'
                    r'&txt_numero_sequencial={sequencial}'
                    r'&txt_numero_ano={ano}"'
                    r' target="_blank">{processo}</a>').format(processo=self.num_processo_sf,**m.groupdict())
        return self.num_processo_sf

    def save(self, *args, **kwargs):
        self.conveniada = self.data_retorno_assinatura is not None
        self.equipada = self.data_termo_aceite is not None
        super(Convenio, self).save(*args, **kwargs)

    class Meta:
        get_latest_by = 'id'
        ordering = ('id',)
        verbose_name = _(u'convênio')

    def __unicode__(self):
        # if self.data_retorno_assinatura is not None:
        #     return _(u"Convênio {project} nº {number} assinado em {date}. Status: {status}".format(
        #         number=self.num_convenio,
        #         project=self.projeto.sigla,
        #         date=self.data_retorno_assinatura,
        #         status=self.get_status()))
        # else:
        #     return _(u"Adesão ao projeto %(project)s, em %(date)s") % dict(
        #         project=self.projeto.sigla,
        #         date=self.data_adesao)

        if ((self.data_retorno_assinatura is None) and
            (self.equipada and self.data_termo_aceite is not None)):
            return _(u"Convênio nº {number} - equipada em {date} pelo {project}"
                     ).format(number=self.num_convenio,
                              date=self.data_termo_aceite.strftime('%d/%m/%Y'),
                              project=self.projeto.sigla)
        elif self.data_retorno_assinatura is None:
            return _(u"Convênio nº {number} - adesão ao projeto {project}, "
                     u"em {date}").format(number=self.num_convenio,
                                          project=self.projeto.sigla,
                                          date=self.data_adesao)
        if ((self.data_retorno_assinatura is not None) and not
            (self.equipada and self.data_termo_aceite is not None)):
            return _(u"Convênio nº {number} - conveniada ao {project} em "
                     u"{date}. Status: {status}").format(
                         number=self.num_convenio,
                         project=self.projeto.sigla,
                         date=self.data_retorno_assinatura.strftime('%d/%m/%Y'),
                         status=self.get_status())
        if ((self.data_retorno_assinatura is not None) and
            (self.equipada and self.data_termo_aceite is not None)):
            return _(u"Convẽnio nº {number} - conveniada ao {project} em {date}"
                     u" e equipada em {equipped_date}. Status: {status}"
                     ).format(number=self.num_convenio,
                              project=self.projeto.sigla,
                              date=self.data_retorno_assinatura.strftime(
                                  '%d/%m/%Y'),
                              equipped_date=self.data_termo_aceite.strftime(
                                  '%d/%m/%Y'),
                              status=self.get_status())

class EquipamentoPrevisto(models.Model):

    """ Modelo utilizado para registrar os equipamentos
    disponibilizados para as Casas Legislativas
    (foi usado na prmeira etapa do programa)
    """
    convenio = models.ForeignKey(
        Convenio,
        on_delete=models.CASCADE,
        verbose_name=_(u'convênio')
    )
    equipamento = models.ForeignKey(
        'inventario.Equipamento',
        on_delete=models.CASCADE
    )
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
    convenio = models.ForeignKey(
        Convenio,
        on_delete=models.CASCADE,
        verbose_name=_(u'convênio')
    )
    # caminho no sistema para o documento anexo
    arquivo = models.FileField(upload_to='apps/convenios/anexo/arquivo', max_length=500)
    descricao = models.CharField(_(u'descrição'), max_length='70')
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
    sigla = models.CharField(max_length='10')
    nome = models.CharField(max_length='100')

    def __unicode__(self):
        return unicode(self.sigla)


class Tramitacao(models.Model):

    """ Modelo para registrar as vias do processo de convênio e a Unidade
    responsável pelo tramite (ex. colher assinaturas do secretário do senado)
    """
    convenio = models.ForeignKey(
        Convenio,
        on_delete=models.CASCADE,
        verbose_name=_(u'convênio')
    )
    unid_admin = models.ForeignKey(
        UnidadeAdministrativa,
        on_delete=models.PROTECT,
        verbose_name=_(u'Unidade Administrativa')
    )
    data = models.DateField()
    observacao = models.CharField(
        _(u'observação'),
        max_length='512',
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
