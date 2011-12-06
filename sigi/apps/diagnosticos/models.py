# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.utils import SearchField
from sigi.apps.utils.email import enviar_email
from eav.models import BaseChoice, BaseEntity, BaseSchema, BaseAttribute


class Diagnostico(BaseEntity):
    """ Modelo para representar unm diagnostico realizado
    em uma Casa Legislativa
    """
    casa_legislativa = models.ForeignKey(
        'casas.CasaLegislativa',
        verbose_name='Casa Legislativa')

    # campo de busca em caixa baixa e sem acento
    search_text = SearchField(field_names=['casa_legislativa'])
    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True
    data_visita_inicio = models.DateField(
        u'data inicial da visita',
        null=True,
        blank=True,
    )
    data_visita_fim = models.DateField(
        u'data final da visita',
        null=True,
        blank=True,
    )
    publicado = models.BooleanField(default=False)
    data_publicacao = models.DateField(
        u'data de publicação do diagnóstico',
        null=True,
        blank=True,
    )

    responsavel = models.ForeignKey('servidores.Servidor',
        verbose_name=u'responsável')

    class Meta:
        verbose_name, verbose_name_plural = u'diagnóstico', u'diagnósticos'

    @property
    def membros(self):
        """ Retorna a lista de membros do diagnostico,
        isto é responsavel + equipe
        """
        membros = set([self.responsavel])
        for equipe in self.equipe_set.all():
            membros.add(equipe.membro)
        return list(membros)

    @property
    def contatos_respondidos(self):
        """Retorna uma lista de contatos que foram
        respondidos
        """
        casa_legislativa = CasaLegislativa.objects.get(
            pk=self.casa_legislativa.id)
        categoria_com_respostas = set(casa_legislativa.funcionario_set.all())

        return list(categoria_com_respostas)

    @property
    def categorias_respondidas(self):
        """ Retorna uma listas das categorias dinamicas que tem
        ao menos uma resposta
        """

        # obtem todas as respostas dinamicas desse diagnostico
        respostas = Resposta.objects.filter(entity_id=self.id).all()

        # unifica as categorias das perguntas dessas respostas
        categoria_com_respostas = set([r.schema.choices.all() for r in respostas])

        return list(categoria_com_respostas)

    def email_diagnostico_publicado(self, from_email, host):
        """Enviando email quando o diagnóstico for publicado. Os
        argumentos acima são:
            * from_email - Email de remetente
            * host - O Host do sistema, para ser usado na
            construção do endereço do diagnóstico
        """
        enviar_email(from_email, u"Diagnóstico publicado",
            'diagnosticos/email_diagnostico_publicado.txt',
            {
                'responsavel': self.responsavel.nome_completo,
                'casa_legislativa': self.casa_legislativa,
                'data_diagnostico': self.data_questionario,
                'host': host,
                'url_diagnostico': self.get_absolute_url(),
                'status': u"Publicado",
            })

    def email_diagnostico_alterado(self, from_email, host):
        """Enviando email quando o status do diagnóstico
        for alterado. Os argumentos acima são:
            * from_email - Email do destinatário
            * host - O Host do sistema, para ser usado na
            construção do endereço do diagnóstico
        """
        enviar_email(from_email, u"Diagnóstico alterado",
            'diagnosticos/email_diagnostico_alterado.txt',
            {
                'servidor': self.responsavel.nome_completo,
                'casa_legislativa': self.casa_legislativa,
                'data_diagnostico': self.data_questionario,
                'host': host,
                'url_diagnostico': self.get_absolute_url,
                'status': "Alterado",
            })

    @classmethod
    def get_schemata_for_model(self):
        return Pergunta.objects.all()

    def __unicode__(self):
        return str(self.casa_legislativa).decode('utf8')

    def get_absolute_url(self):
        return "/diagnosticos/diagnostico/%i/" % (self.id, )


class Categoria(models.Model):
    """ Modelo para representar a categoria de uma pergunta
    e sua ordem na hora de exibir no formulário
    """
    nome = models.CharField(max_length=255)

    class Meta:
        ordering = ('nome',)

    def __unicode__(self):
        return self.nome


class Pergunta(BaseSchema):
    """ Modelo que representa uma pergunta no questionário
    e sua ordem dentro da categoria

    Uma pergunta tem o nome e o tipo da resposta
    """
    categoria = models.ForeignKey(Categoria, related_name='perguntas')

    class Meta:
        ordering = ('title',)
        verbose_name, verbose_name_plural = 'pergunta', 'perguntas'


class Escolha(BaseChoice):
    """ Perguntas de multiplas escolhas tem as opções
    cadastradas neste modelo
    """
    schema = models.ForeignKey(Pergunta,
        related_name='choices', verbose_name='pergunta')
    schema_to_open = models.ForeignKey(Pergunta, related_name='',
        verbose_name='pergunta para abrir', blank=True, null=True)

    class Meta:
        verbose_name, verbose_name_plural = 'escolha', 'escolhas'


class Resposta(BaseAttribute):
    """ Modelo para guardar as respostas das perguntas
    de um diagnosico
    """
    schema = models.ForeignKey(Pergunta, related_name='attrs',
        verbose_name='pergunta')
    choice = models.ForeignKey(Escolha, verbose_name='escolha',
        blank=True, null=True)

    class Meta:
        verbose_name, verbose_name_plural = 'resposta', 'respostas'


class Equipe(models.Model):
    """ Modelo que representa a equipe de um diagnóstico
    """
    diagnostico = models.ForeignKey(Diagnostico)
    membro = models.ForeignKey('servidores.Servidor')

    class Meta:
        verbose_name, verbose_name_plural = 'equipe', 'equipe'

    def __unicode__(self):
        return str(self.membro)


class Anexo(models.Model):
    """ Modelo para representar os documentos levantados
    no processo de diagnóstico. Podem ser fotos, contratos, etc.
    """
    diagnostico = models.ForeignKey(Diagnostico, verbose_name=u'diagnóstico')
    arquivo = models.FileField(upload_to='apps/diagnostico/anexo/arquivo',)
    descricao = models.CharField('descrição', max_length='70')
    data_pub = models.DateTimeField('data da publicação do anexo',
        default=datetime.now)

    class Meta:
        ordering = ('-data_pub',)

    def __unicode__(self):
        return unicode(self.arquivo.name)
