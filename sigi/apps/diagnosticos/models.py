# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from sigi.apps.utils import SearchField
from eav.models import BaseChoice, BaseEntity, BaseSchema, BaseAttribute


class Diagnostico(BaseEntity):
    """ Modelo para representar unm diagnostico realizado
    em uma Casa Legislativa
    """
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa'
    )
    # campo de busca em caixa baixa e sem acento
    search_text = SearchField(field_names=['casa_legislativa'])
    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True
    data_visita = models.DateField(
        'data da visita',
        null=True,
        blank=True,
    )
    data_questionario = models.DateField(
        'data do questionario',
        null=True,
        blank=True,
        help_text='Convênio firmado.'
    )
    data_relatorio_questionario = models.DateField(
        'data do relatório do questionario',
        null=True,
        blank=True
    )
    data_termo_aceite = models.DateField(
        'Equipadas',
        null=True,
        blank=True,
        help_text='Equipamentos recebidos.'
    )

    class Meta:
        verbose_name, verbose_name_plural = u'diagnóstico', u'diagnósticos'

    @classmethod
    def get_schemata_for_model(self):
        return Pergunta.objects.all()

    def __unicode__(self):
        return str(self.casa_legislativa)


class Categoria(models.Model):
    """ Modelo para representar a categoria de uma pergunta
    e sua ordem na hora de exibir no formulário
    """

    nome = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nome


class Pergunta(BaseSchema):
    """ Modelo que representa uma pergunta no questionário
    e sua ordem dentro da categoria

    Uma pergunta tem o nome e o tipo da resposta
    """
    categoria = models.ForeignKey(Categoria)

    class Meta:
        ordering = ('title',)
        verbose_name, verbose_name_plural = 'pergunta', 'perguntas'


class Escolha(BaseChoice):
    """ Perguntas de multiplas escolhas tem as opções
    cadastradas neste modelo
    """
    schema = models.ForeignKey(Pergunta, related_name='choices', verbose_name='pergunta')
    schema_to_open = models.ForeignKey(Pergunta, related_name='', verbose_name='pergunta para abrir', blank=True, null=True)

    class Meta:
        verbose_name, verbose_name_plural = 'escolha', 'escolhas'


class Resposta(BaseAttribute):
    """ Modelo para guardar as respostas das perguntas
    de um diagnosico
    """
    schema = models.ForeignKey(Pergunta, related_name='attrs', verbose_name='pergunta')
    choice = models.ForeignKey(Escolha, verbose_name='escolha', blank=True, null=True)

    class Meta:
        verbose_name, verbose_name_plural = 'resposta', 'respostas'


class Equipe(models.Model):
    """ Modelo que representa a equipe de um diagnóstico
    """
    diagnostico = models.ForeignKey(Diagnostico)
    membro = models.ForeignKey('servidores.Servidor')
    # verdadeiro se o servidor é repsonsável por chefiar a equipe
    is_chefe = models.BooleanField()

    def __unicode__(self):
        return str(self.id)


class Anexo(models.Model):
    """ Modelo para representar os documentos levantados
    no processo de diagnóstico. Podem ser fotos, contratos, etc.
    """
    diagnostico = models.ForeignKey(Diagnostico, verbose_name=u'diagnóstico')
    arquivo = models.FileField(upload_to='apps/diagnostico/anexo/arquivo',)
    descricao = models.CharField('descrição', max_length='70')
    data_pub = models.DateTimeField(
        'data da publicação do anexo',
        default=datetime.now
    )

    class Meta:
        ordering = ('-data_pub',)

    def __unicode__(self):
        return unicode(self.arquivo.name)
