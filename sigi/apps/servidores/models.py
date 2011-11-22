# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class Subsecretaria(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
    responsavel = models.ForeignKey('servidores.Servidor', related_name='diretor')

    class Meta:
        ordering = ('nome',)

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.nome), unicode(self.sigla))

class Servico(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
    subsecretaria = models.ForeignKey(Subsecretaria)
    responsavel = models.ForeignKey('servidores.Servidor', related_name='chefe')

    class Meta:
        ordering = ('nome',)
        verbose_name = 'serviço'
        verbose_name_plural = 'serviços'

    def __unicode__(self):
        return '%s (%s)' % (unicode(self.nome), unicode(self.sigla))

class Servidor(models.Model):
    SEXO_CHOICES = (
        ('M', u'Masculino'),
        ('F', u'Feminino'),
    )
    TURNO_CHOICES = (
        ('M', u'Manhã'),
        ('T', u'Tarde'),
        ('N', u'Noite'),
    )
    nome_completo = models.CharField(max_length=128)
    nome_completo.alphabetic_filter = True
    user = models.ForeignKey(User, unique=True)
    apelido = models.CharField(max_length=50, blank=True)
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
    email = models.EmailField('e-mail', blank=True, null=True)
    servico = models.ForeignKey('servidores.Servico', blank=True, null=True)
    is_chefe = models.BooleanField()
    matricula = models.CharField(u'matrícula', max_length=25, blank=True, null=True)
    turno= models.CharField(
        max_length=1,
        choices=TURNO_CHOICES,
        blank=True,
        null=True,
    )
    data_entrada = models.DateField(u'data de entrada', blank=True, null=True)
    data_saida = models.DateField(u'data de saída', blank=True, null=True)
    data_nomeacao = models.DateField(u'data de nomeação', blank=True, null=True)
    ato_exoneracao = models.CharField(u'ato de exoneração',max_length=150, blank=True, null=True)
    cpf = models.CharField('CPF', max_length=11, blank=True, null=True)
    rg = models.CharField('RG', max_length=25, blank=True, null=True)
    obs = models.TextField(u'observação', blank=True, null=True)
    apontamentos = models.TextField(u'apontamentos', blank=True, null=True)

    #endereco = models.ForeignKey('contatos.Endereco', blank=True, null=True)
    endereco = generic.GenericRelation('contatos.Endereco')
    telefones = generic.GenericRelation('contatos.Telefone')
    ramal = models.IntegerField('ramal', blank=True, null=True)

    class Meta:
        ordering = ('nome_completo',)
        verbose_name_plural = 'servidores'

    def __unicode__(self):
        return self.nome_completo

class Funcao(models.Model):
    servidor = models.ForeignKey(Servidor)
    funcao = models.CharField(max_length=50)
    cargo = models.CharField(max_length=50, blank=True, null=True)
    inicio_funcao = models.DateField(u'início da função')
    fim_funcao = models.DateField(u'fim da função', blank=True, null=True)
    descricao = models.TextField(u'descrição', blank=True, null=True)

    bap_entrada = models.CharField('BAP de entrada',max_length=50, blank=True, null=True)
    data_bap_entrada = models.DateField('data BAP de entrada', blank=True, null=True)

    bap_saida = models.CharField(u'BAP de saída',max_length=50, blank=True, null=True)
    data_bap_saida = models.DateField(u'data BAP de saída', blank=True, null=True)

    class Meta:
        verbose_name = u'função'
        verbose_name_plural = u'funções'

    def __unicode__(self):
        return str(self.id)


class Licenca(models.Model):
    servidor = models.ForeignKey(Servidor)
    inicio_licenca = models.DateField(u'início da licença')
    fim_licenca = models.DateField(u'fim da licença')
    obs = models.TextField(u'observação', blank=True, null=True)

    class Meta:
        verbose_name = u'licença'
        verbose_name_plural = u'licenças'

    def __unicode__(self):
        return str(self.id)

class Ferias(models.Model):
    servidor = models.ForeignKey(Servidor)
    inicio_ferias = models.DateField(u'início das férias')
    fim_ferias = models.DateField(u'fim das férias')
    obs = models.TextField(u'observação', blank=True, null=True)

    class Meta:
        verbose_name = u'férias'
        verbose_name_plural = u'férias'

    def __unicode__(self):
        return str(self.id)
