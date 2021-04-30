# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

class Servico(models.Model):
    nome = models.CharField(_(u'Setor'), max_length=250, null=True)
    sigla = models.CharField(max_length=10, null=True)
    subordinado = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_(u"subordinado a")
    )
    responsavel = models.ForeignKey(
        'servidores.Servidor',
        on_delete=models.SET_NULL,
        related_name='chefe',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('-subordinado__sigla', 'nome',)
        verbose_name = _(u'serviço')
        verbose_name_plural = _(u'serviços')

    def __unicode__(self):
        return u"{sigla} - {nome}".format(sigla=self.sigla, nome=self.nome)

class Servidor(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    nome_completo = models.CharField(max_length=128)
    apelido = models.CharField(max_length=50, blank=True)
    foto = models.ImageField(
        upload_to='fotos/servidores',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    servico = models.ForeignKey(
        Servico,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    externo = models.BooleanField(_(u"colaborador externo"), default=False)
    orgao_origem = models.CharField(
        _(u"órgão de origem, "),
        max_length=100, blank=True
    )
    qualificacoes = models.TextField(_(u"qualificações"), blank=True)

    class Meta:
        ordering = ('nome_completo',)
        verbose_name_plural = 'servidores'

    def __unicode__(self):
        return self.nome_completo

    def save(self, *args, **kwargs):
        if self.user is not None:
            Servidor.objects.filter(user=self.user).update(user=None)
        return super(Servidor, self).save(*args, **kwargs)

# Soluçao alternativa para extender o usuário do django
# Acessa do servidor de um objeto user criando um profile
# baseado nos dados do LDAP
User.servidor = property(lambda user: Servidor.objects.get(user=user))

# Sinal para ao criar um usuário criar um servidor
# baseado no nome contino no LDAP
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Servidor.objects.create(
            user=instance,
            nome_completo="%s %s" % (instance.first_name, instance.last_name)
        )

post_save.connect(create_user_profile, sender=User)