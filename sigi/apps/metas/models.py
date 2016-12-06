# -*- coding: utf-8 -*-
from datetime import date

from django.db import models
from django.utils.translation import ugettext as _

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.convenios.models import Convenio, Projeto
from sigi.apps.diagnosticos.models import Diagnostico
from sigi.apps.financeiro.models import Desembolso


class Meta(models.Model):
    ALGORITMO_CHOICES = (
        ('SUM_GASTOS', _(u'Soma dos desembolsos')),
        ('COUNT_EQUI', _(u'Quantidade de casas equipadas')),
        ('COUNT_ADER', _(u'Quantidade de casas aderidas')),
        ('COUNT_DIAG', _(u'Quantidade de casas diagnosticadas')),
        ('COUNT_PDIR', _(u'Quantidade de planos diretores')),
        ('COUNT_CONV', _(u'Quantidade de casas conveniadas')),
    )
    projeto = models.ForeignKey(Projeto, verbose_name=_(u'Projeto'), help_text=_(u'Projeto ao qual a meta se refere'))
    titulo = models.CharField(_(u'Título'), max_length=40, help_text=_(u'Título da meta que aparecerá no dashboard'))
    descricao = models.TextField(_(u'Descrição'))
    data_inicio = models.DateField(_(u'Data inicial'), help_text=_(u'Início do período de cômputo da meta'))
    data_fim = models.DateField(_(u'Data final'), help_text=_(u'Prazo final para cumprimento da meta'))
    algoritmo = models.CharField(_(u'Algoritmo de cálculo'), max_length=10, choices=ALGORITMO_CHOICES)
    valor_meta = models.FloatField(_(u'Valor da meta'), help_text=_(u'Valor que deve ser atingido até o prazo final da meta'))

    class Meta:
        verbose_name = _(u'Meta BID')
        verbose_name_plural = _(u'Metas BID')

    def __unicode__(self):
        return self.titulo

    @property
    def valor_executado(self):
        """
        Calcula o valor executado da meta
        """
        algoritmo = self.algoritmo.lower()
        valor = getattr(self, algoritmo)()
        try:
            valor = float(valor)
        except:
            valor = 0.0
        return valor

    @property
    def percentual_concluido(self):
        return round(float(self.valor_executado) / float(self.valor_meta) * 100.0, 2)

    @property
    def valor_desejado(self):
        total_dias = (self.data_fim - self.data_inicio).days + 1
        dias_gastos = (date.today() - self.data_inicio).days + 1
        meta_dia = self.valor_meta / total_dias
        return meta_dia * dias_gastos

    @property
    def percentual_desejado_low(self):
        return (self.valor_desejado / self.valor_meta) - 0.05  # 5% abaixo do desejado

    @property
    def percentual_desejado_high(self):
        return (self.valor_desejado / self.valor_meta) + 0.05  # 5% acima do desejado

    @property
    def saude(self):
        percentual_concluido = self.percentual_concluido / 100.0
        if percentual_concluido >= 1:
            return 'A2BBED'  # Blue

        if percentual_concluido > self.percentual_desejado_high:
            return '89D7AF'  # Green

        if percentual_concluido > self.percentual_desejado_low:
            return 'FFDB6E'  # Orange

        return 'E74A69'  # Red

    def sum_gastos(self):
        valor = Desembolso.objects.filter(projeto=self.projeto, data__gte=self.data_inicio, data__lte=self.data_fim) \
            .aggregate(total_dolar=models.Sum('valor_dolar'))
        valor = valor['total_dolar']
        return valor

    def count_equi(self):
        valor = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM', equipada=True, projeto__pk=3, data_termo_aceite__gte=self.data_inicio, data_termo_aceite__lte=self.data_fim).exclude(data_termo_aceite=None).count()
        return valor

    def count_ader(self):
        valor = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM', projeto=self.projeto, data_adesao__gte=self.data_inicio,
                                        data_adesao__lte=self.data_fim).exclude(data_adesao=None).count()
        return valor

    def count_diag(self):
        valor = Diagnostico.objects.filter(data_visita_inicio__gte=self.data_inicio, data_visita_inicio__lte=self.data_fim,
                                           publicado=True).count()
        return valor

    def count_pdir(self):
        valor = PlanoDiretor.objects.filter(projeto=self.projeto, data_entrega__gte=self.data_inicio,
                                            data_entrega__lte=self.data_fim).count()
        return valor

    def count_conv(self):
        valor = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM', projeto=self.projeto, data_retorno_assinatura__gte=self.data_inicio, data_retorno_assinatura__lte=self.data_fim).exclude(data_retorno_assinatura=None).count()
        return valor


class PlanoDiretor(models.Model):
    STATUS_CHOICE = (
        ('E', _(u'Entregue')),
        ('I', _(u'Implantado')),
    )
    projeto = models.ForeignKey(Projeto, verbose_name=_(u'Projeto'))
    casa_legislativa = models.ForeignKey(CasaLegislativa, verbose_name=_(u'Casa Legislativa'))
    casa_legislativa.casa_uf_filter = True
    status = models.CharField(_(u'Status'), max_length=1, choices=STATUS_CHOICE, default='E')
    data_entrega = models.DateField(_(u'Data de entrega'), blank=True, null=True)
    data_implantacao = models.DateField(_(u'Data de implantação'), blank=True, null=True)

    class Meta:
        verbose_name = _(u'Plano Diretor')
        verbose_name_plural = _(u'Planos Diretores')

    def __unicode__(self):
        return self.casa_legislativa.nome
