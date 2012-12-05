# -*- coding: utf-8 -*-
from datetime import date, datetime
from django.db import models
from sigi.apps.convenios.models import Projeto, Convenio
from sigi.apps.diagnosticos.models import Diagnostico
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.financeiro.models import Desembolso

class Meta(models.Model):
    ALGORITMO_CHOICES = (
        ('SUM_GASTOS', u'Soma dos desembolsos'),
        ('COUNT_EQUI', u'Quantidade de casas equipadas'),
        ('COUNT_ADER', u'Quantidade de casas aderidas'),
        ('COUNT_DIAG', u'Quantidade de casas diagnosticadas'),
        ('COUNT_PDIR', u'Quantidade de planos diretores'),
        ('COUNT_CONV', u'Quantidade de casas conveniadas'),
    )
    projeto = models.ForeignKey(Projeto, verbose_name=u'Projeto', help_text=u'Projeto ao qual a meta se refere') 
    titulo = models.CharField(u'Título', max_length=40, help_text=u'Título da meta que aparecerá no dashboard')
    descricao = models.TextField(u'Descrição')
    data_inicio = models.DateField(u'Data inicial', help_text=u'Início do período de cômputo da meta')
    data_fim = models.DateField(u'Data final', help_text=u'Prazo final para cumprimento da meta')
    algoritmo = models.CharField(u'Algoritmo de cálculo', max_length=10, choices=ALGORITMO_CHOICES)
    valor_meta = models.FloatField(u'Valor da meta', help_text=u'Valor que deve ser atingido até o prazo final da meta')
    hora_ultimo_calculo = models.DateTimeField(u'Data último calculo', blank=True, null=True, editable=False,
                            help_text=u'Momento em que a meta foi calculada pela última vez')
    valor_ultimo_calculo = models.FloatField(u'Valor último cálculo', blank=True, null=True, editable=False,
                            help_text=u'Valor do último calculo da meta')
    
    class Meta:
        verbose_name = 'Meta BID'
        verbose_name_plural = 'Metas BID'
    
    def __unicode__(self):
        return self.titulo;
    
    @property
    def percentual_concluido(self):
        return round(self.valor_ultimo_calculo / self.valor_meta * 100.0, 2)
    
    @property
    def saude(self):
        if self.valor_ultimo_calculo >= self.valor_meta:
            return 'green'

        total_meses = (self.data_fim - self.data_inicio).days / 30
        meses_gastos = (date.today() - self.data_inicio).days / 30
        meta_mensal = self.valor_meta / total_meses
        valor_desejado = meta_mensal * meses_gastos
        
        if self.valor_ultimo_calculo > (valor_desejado * 1.1):
            return 'green'
        
        if self.valor_ultimo_calculo > (valor_desejado * 0.9):
            return 'orange'
        
        return 'red'
        
    
    def calcular(self):
        """
        Calcula o valor da meta e salva o resultado para uso futuro
        """
        algoritmo = self.algoritmo.lower()
        valor = getattr(self, algoritmo)()
        self.hora_ultimo_calculo = datetime.now()
        self.valor_ultimo_calculo = valor
        self.save() 
    
    def sum_gastos(self):
        #TODO: Para fazer este algoritmo, precisamos criar registro de desembolsos no sistema financeiro
        valor = Desembolso.objects.filter(projeto=self.projeto, data__gte=self.data_inicio, data__lte=self.data_fim) \
                    .aggregate(total_dolar=models.Sum('valor_dolar')) 
        return valor['total_dolar']
    
    def count_equi(self):
        valor = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM', equipada=True, projeto__pk=3, data_termo_aceite__gte=
                    self.data_inicio, data_termo_aceite__lte=self.data_fim).exclude(data_termo_aceite=None).count()
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
        valor = PlanoDiretor.objects.filter(projeto=self.projeto, status='A', data_assinatura__gte=self.data_inicio,
                    data_assinatura__lte=self.data_fim).exclude(data_assinatura=None).count()
        return valor
    
    def count_conv(self):
        valor = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM', projeto=self.projeto, data_retorno_assinatura__gte=
                    self.data_inicio, data_retorno_assinatura__lte=self.data_fim).exclude(data_retorno_assinatura=None).count()
        return valor
    
class PlanoDiretor(models.Model):
    STATUS_CHOICE = (
        ('E', u'Em elaboração'),
        ('A', u'Aceito'),
        ('R', u'Rejeitado'),
    )
    projeto = models.ForeignKey(Projeto, verbose_name=u'Projeto')
    casa_legislativa = models.ForeignKey(CasaLegislativa, verbose_name=u'Casa legislativa')
    status = models.CharField(u'Status', max_length=1, choices=STATUS_CHOICE, default='E')
    data_elaboracao = models.DateField(u'Data de elaboração')
    data_assinatura = models.DateField(u'Data de assinatura', blank=True, null=True)
    data_rejeicao = models.DateField(u'Data da rejeição', blank=True, null=True)

    class Meta:
        verbose_name = 'Plano Diretor'
        verbose_name_plural = 'Planos Diretores'
    
    def __unicode__(self):
        return self.casa_legislativa.nome ;
    