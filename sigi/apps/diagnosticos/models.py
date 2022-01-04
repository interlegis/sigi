# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.utils.translation import gettext as _
from eav.models import BaseChoice, BaseEntity, BaseSchema, BaseAttribute

from sigi.apps.utils import SearchField
from sigi.apps.utils.email import enviar_email


class Diagnostico(BaseEntity):

    """ Modelo para representar unm diagnostico realizado
    em uma Casa Legislativa
    """
    casa_legislativa = models.ForeignKey(
        'casas.Orgao',
        on_delete=models.PROTECT,
        verbose_name=_('Casa Legislativa')
    )

    # campo de busca em caixa baixa e sem acento
    search_text = SearchField(field_names=['casa_legislativa'])
    # casa_legislativa.casa_uf_filter = True
    # casa_legislativa.casa_tipo_filter = True
    data_visita_inicio = models.DateField(
        'data inicial da visita',
        null=True,
        blank=True,
    )
    data_visita_fim = models.DateField(
        'data final da visita',
        null=True,
        blank=True,
    )
    publicado = models.BooleanField(default=False)
    data_publicacao = models.DateField(
        'data de publicação do diagnóstico',
        null=True,
        blank=True,
    )

    responsavel = models.ForeignKey(
        'servidores.Servidor',
        on_delete=models.PROTECT,
        verbose_name=_('responsável')
    )

    class Meta:
        verbose_name, verbose_name_plural = _('diagnóstico'), _('diagnósticos')

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
        return list(self.casa_legislativa.funcionario_set.all())

    @property
    def categorias_respondidas(self):
        """ Retorna uma listas das categorias dinamicas que tem
        ao menos uma resposta
        """
        # unifica as categorias das perguntas dessas respostas
        categoria_com_respostas = set([r.schema.categoria for r in self._get_respostas()])

        return list(categoria_com_respostas)

    def _get_respostas(self):
        # obtem todas as respostas dinamicas desse diagnostico
        respostas = Resposta.objects.filter(entity_id=self.id).all()

        # remove as respostas nulas ou em branco
        return [r for r in respostas if r._get_value()]

    def email_diagnostico_publicado(self, from_email, host):
        """Enviando email quando o diagnóstico for publicado. Os
        argumentos acima são:
            * from_email - Email de remetente
            * host - O Host do sistema, para ser usado na
            construção do endereço do diagnóstico
        """
        enviar_email(from_email, _("Diagnóstico publicado"),
                     'diagnosticos/email_diagnostico_publicado.txt',
                     {
                         'responsavel': self.responsavel.nome_completo,
                         'casa_legislativa': self.casa_legislativa,
                         'data_diagnostico': self.data_visita_inicio,
                         'host': host,
                         'url_diagnostico': self.get_absolute_url(),
                         'status': _("Publicado"),
        })

    def email_diagnostico_alterado(self, from_email, host):
        """Enviando email quando o status do diagnóstico
        for alterado. Os argumentos acima são:
            * from_email - Email do destinatário
            * host - O Host do sistema, para ser usado na
            construção do endereço do diagnóstico
        """
        enviar_email(from_email, _("Diagnóstico alterado"),
                     'diagnosticos/email_diagnostico_alterado.txt',
                     {
                         'servidor': self.responsavel.nome_completo,
                         'casa_legislativa': self.casa_legislativa,
                         'data_diagnostico': self.data_visita_inicio,
                         'host': host,
                         'url_diagnostico': self.get_absolute_url(),
                         'status': _("Alterado"),
        })

    def get_schemata(self, category=None, *args, **kwargs):
        """ Se existir uma categoria retorna apenas as questões dessa.
        """
        schemas = super(Diagnostico, self).get_schemata(*args, **kwargs)
        if category:
            schemas = [s for s in schemas if s.categoria_id == category]
            schemas = sorted(schemas, lambda x, y: cmp(x.title, y.title))

        return schemas

    @classmethod
    def get_schemata_for_model(self):
        return Pergunta.objects.all()

    def __unicode__(self):
        return str(self.casa_legislativa).decode('utf8')

    def get_absolute_url(self):
        return "/diagnosticos/diagnostico/%i.pdf" % (self.id, )


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
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='perguntas'
    )

    def group_choices(self):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute("""
          SELECT choice_id, sum(1)
          FROM diagnosticos_resposta
          WHERE schema_id=%s and choice_id is not null
          GROUP BY choice_id;
        """, [self.id])

        return [
            (Escolha.objects.get(id=int(row[0])), row[1])
            for row in cursor.fetchall()
        ]

    def total_anwsers(self):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute("""
          SELECT sum(1)
          FROM diagnosticos_resposta
          WHERE schema_id=%s
        """, [self.id])

        return cursor.fetchone()

    class Meta:
        ordering = ('title',)
        verbose_name, verbose_name_plural = _('pergunta'), _('perguntas')


class Escolha(BaseChoice):

    """ Perguntas de multiplas escolhas tem as opções
    cadastradas neste modelo
    """
    schema = models.ForeignKey(
        Pergunta,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name=_('pergunta')
    )
    schema_to_open = models.ForeignKey(
        Pergunta,
        on_delete=models.SET_NULL,
        related_name='abre_por',
        verbose_name=_('pergunta para abrir'),
        blank=True,
        null=True
    )
    ordem = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ('schema', 'ordem')
        verbose_name, verbose_name_plural = _('escolha'), _('escolhas')


class Resposta(BaseAttribute):

    """ Modelo para guardar as respostas das perguntas
    de um diagnosico
    """
    schema = models.ForeignKey(
        Pergunta,
        on_delete=models.PROTECT,
        related_name='attrs',
        verbose_name=_('pergunta')
    )
    choice = models.ForeignKey(
        Escolha,
        on_delete=models.PROTECT,
        verbose_name=_('escolha'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name, verbose_name_plural = _('resposta'), _('respostas')


class Equipe(models.Model):

    """ Modelo que representa a equipe de um diagnóstico
    """
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE)
    membro = models.ForeignKey(
        'servidores.Servidor',
        on_delete=models.PROTECT
    )

    class Meta:
        verbose_name, verbose_name_plural = _('equipe'), _('equipe')

    def __unicode__(self):
        return self.membro.__unicode__()


class Anexo(models.Model):

    """ Modelo para representar os documentos levantados
    no processo de diagnóstico. Podem ser fotos, contratos, etc.
    """
    diagnostico = models.ForeignKey(
        Diagnostico,
        on_delete=models.CASCADE,
        verbose_name='diagnóstico'
    )
    arquivo = models.FileField(upload_to='apps/diagnostico/anexo/arquivo', max_length=500)
    descricao = models.CharField(_('descrição'), max_length='70')
    data_pub = models.DateTimeField(_('data da publicação do anexo'),
                                    default=datetime.now)

    class Meta:
        ordering = ('-data_pub',)

    def __unicode__(self):
        return unicode(self.arquivo.name)
