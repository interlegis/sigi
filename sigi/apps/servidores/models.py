# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _


class Subsecretaria(models.Model):

    """ Modelo para representação das Subsecretarias do Interlegis
    """

    nome = models.CharField(max_length=250, null=True)
    sigla = models.CharField(max_length=10, null=True)
    # servidor responsavel por dirigir a Subsecretaria
    responsavel = models.ForeignKey('servidores.Servidor', related_name='diretor', null=True)

    class Meta:
        ordering = ('nome',)

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.nome), unicode(self.sigla))


class Servico(models.Model):

    """ Modelo para representação dos Serviços de uma Subsecretaria
    """

    nome = models.CharField(_(u'Setor'), max_length=250, null=True)
    sigla = models.CharField(max_length=10, null=True)
    subsecretaria = models.ForeignKey(Subsecretaria, null=True)
    # servidor responsavel por chefiar o serviço
    responsavel = models.ForeignKey('servidores.Servidor', related_name='chefe', null=True)

    class Meta:
        ordering = ('nome',)
        verbose_name = _(u'serviço')
        verbose_name_plural = _(u'serviços')

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.nome), unicode(self.sigla))


class Servidor(models.Model):

    """ Modelo para representação de um Servidor.

    Um servidor pertence a um Serviço e uma Subsecretaria os campos
    deste modelo são referente as informações básicas de cadastro.
    """

    SEXO_CHOICES = (
        ('M', u'Masculino'),
        ('F', u'Feminino'),
    )

    TURNO_CHOICES = (
        ('M', u'Manhã'),
        ('T', u'Tarde'),
        ('N', u'Noite'),
    )

    # usuario responsavel pela autenticação do servidor no sistema
    user = models.ForeignKey(User, unique=True)
    nome_completo = models.CharField(max_length=128)
    apelido = models.CharField(max_length=50, blank=True)
    # caminho no sistema para arquivo com a imagem
    foto = models.ImageField(
        upload_to='fotos/servidores',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        blank=True,
        null=True,
    )
    data_nascimento = models.DateField(
        'data de nascimento',
        blank=True,
        null=True,
    )
    servico = models.ForeignKey('servidores.Servico', blank=True, null=True)
    matricula = models.CharField(u'matrícula', max_length=25, blank=True, null=True)
    turno = models.CharField(
        max_length=1,
        choices=TURNO_CHOICES,
        blank=True,
        null=True,
    )
    de_fora = models.BooleanField(default=False)
    data_nomeacao = models.DateField(u'data de nomeação', blank=True, null=True)
    ato_exoneracao = models.CharField(u'ato de exoneração', max_length=150, blank=True, null=True)
    ato_numero = models.CharField(u'ato de exoneração', max_length=150, blank=True, null=True)
    cpf = models.CharField('CPF', max_length=11, blank=True, null=True)
    rg = models.CharField('RG', max_length=25, blank=True, null=True)
    obs = models.TextField(u'observação', blank=True, null=True)
    apontamentos = models.TextField(u'apontamentos', blank=True, null=True)

    # Informações de contato
    email_pessoal = models.EmailField('email pessoal', blank=True, null=True)
    endereco = fields.GenericRelation('contatos.Endereco')
    telefones = fields.GenericRelation('contatos.Telefone')
    ramal = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        ordering = ('nome_completo',)
        verbose_name_plural = 'servidores'

    def is_chefe(self):
        """ Verifica se o servidor é chefe ou diretor
        """
        pass

    def data_entrada(self):
        """ Verifica a data de entrada da função mais antiga
        """
        pass

    def data_saida(self):
        """ Verifica a data de saída da função mais recente
        de um servidor desativado

        Caso o usuário esteja ativo retorna None
        """
        pass

    @property
    def diagnosticos(self):
        """ Retorna todos os diagnosticos que este servidor
        participa, isto é, como responsavel ou parte da equipe
        """
        diagnosticos = set(self.diagnostico_set.filter(publicado=True).all())

        for equipe in self.equipe_set.all():
            diagnosticos.add(equipe.diagnostico)

        return list(diagnosticos)

    def __unicode__(self):
        return self.nome_completo

# Soluçao alternativa para extender o usuário do django
# Acessa do servidor de um objeto user criando um profile
# baseado nos dados do LDAP

User.servidor = property(lambda user: Servidor.objects.get(user=user))

# Sinal para ao criar um usuário criar um servidor
# baseado no nome contino no LDAP


def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        Servidor.objects.create(
            user=instance,
            nome_completo="%s %s" % (instance.first_name, instance.last_name)
        )

post_save.connect(create_user_profile, sender=User)


class Funcao(models.Model):

    """ Modelo para guardar o histórico de funções dos
    servidores no Interlegis
    """
    servidor = models.ForeignKey(Servidor)
    funcao = models.CharField(max_length=250, null=True)
    cargo = models.CharField(max_length=250, null=True)
    inicio_funcao = models.DateField(u'início da função', null=True)
    fim_funcao = models.DateField(u'fim da função', blank=True, null=True)
    descricao = models.TextField(u'descrição', blank=True, null=True)

    bap_entrada = models.CharField('BAP de entrada', max_length=50, blank=True, null=True)
    data_bap_entrada = models.DateField('data BAP de entrada', blank=True, null=True)

    bap_saida = models.CharField(u'BAP de saída', max_length=50, blank=True, null=True)
    data_bap_saida = models.DateField(u'data BAP de saída', blank=True, null=True)

    class Meta:
        verbose_name = u'função'
        verbose_name_plural = u'funções'

    def __unicode__(self):
        return str(self.id)


class Licenca(models.Model):

    """ Modelo que representa as licenças tiradas pelos servidores
    """
    servidor = models.ForeignKey(Servidor)
    inicio_licenca = models.DateField(u'início da licença')
    fim_licenca = models.DateField(u'fim da licença')
    obs = models.TextField(u'observação', blank=True, null=True)

    class Meta:
        verbose_name = u'licença'
        verbose_name_plural = u'licenças'

    def days():
        """ Calcula a quantidade de dias da licença
        """
        pass

    def __unicode__(self):
        return str(self.id)


class Ferias(models.Model):

    """ Modelo que representa as férias tiradas pelos servidores
    """
    servidor = models.ForeignKey(Servidor)
    inicio_ferias = models.DateField(u'início das férias')
    fim_ferias = models.DateField(u'fim das férias')
    obs = models.TextField(u'observação', blank=True, null=True)

    class Meta:
        verbose_name = u'férias'
        verbose_name_plural = u'férias'

    def days():
        """ Calcula a quantidade de dias das férias
        """
        pass

    def __unicode__(self):
        return str(self.id)
