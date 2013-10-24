# -*- coding: utf-8 -*-
from django.db import models
from sigi.apps.casas.models import CasaLegislativa, Funcionario
from datetime import date
from django.core.mail import send_mail
from sigi.settings import DEFAULT_FROM_EMAIL

class TipoServico(models.Model):
    email_help = '''Use:<br/>
                        {url} para incluir a URL do serviço,<br/>
                        {senha} para incluir a senha inicial do serviço'''
    nome = models.CharField('Nome', max_length=60)
    sigla = models.CharField('Sigla', max_length='12')
    template_email_ativa = models.TextField('Template de email de ativação', help_text = email_help, blank=True)
    template_email_altera = models.TextField('Template de email de alteração', help_text = email_help, blank=True)
    template_email_desativa = models.TextField('Template de email de desativação', help_text = email_help + '<br/>{motivo} para incluir o motivo da desativação do serviço', blank=True)
    
    @property        
    def qtde_casas_atendidas(self):
        u"""Quantidade de casas atendidas"""
        return self.servico_set.filter(data_desativacao=None).count()

    class Meta:
        verbose_name = 'Tipo de serviço'
        verbose_name_plural = 'Tipos de serviço'
    
    def __unicode__(self):
        return self.nome;

class Servico(models.Model):
    casa_legislativa = models.ForeignKey(CasaLegislativa, verbose_name='Casa legislativa')
    tipo_servico = models.ForeignKey(TipoServico, verbose_name='Tipo de serviço')
    contato_tecnico = models.ForeignKey(Funcionario, verbose_name='Contato técnico', related_name='contato_tecnico')
    contato_administrativo = models.ForeignKey(Funcionario, verbose_name='Contato administrativo', related_name='contato_administrativo')
    url = models.URLField('URL do serviço', verify_exists=False, blank=True)
    hospedagem_interlegis = models.BooleanField('Hospedagem no Interlegis?')
    nome_servidor = models.CharField('Hospedado em', max_length=60, blank=True, help_text='Se hospedado no Interlegis, informe o nome do servidor.<br/>Senão, informe o nome do provedor de serviços.')
    porta_servico = models.PositiveSmallIntegerField('Porta de serviço (instância)', blank=True, null=True)
    senha_inicial = models.CharField('Senha inicial', max_length=33, blank=True)
    data_ativacao = models.DateField('Data de ativação', default=date.today)
    data_alteracao = models.DateField('Data da última alteração', blank=True, null=True, auto_now=True)
    data_desativacao = models.DateField('Data de desativação', blank=True, null=True)
    motivo_desativacao = models.TextField('Motivo da desativação', blank=True)
    
    casa_legislativa.casa_uf_filter = True
    
    def __unicode__(self):
        return "%s (%s)" % (self.tipo_servico.nome, 'ativo' if self.data_desativacao is None else 'Desativado')
    
    def save(self, *args, **kwargs):
        # Reter o objeto original para verificar mudanças
        
        if self.id is not None:
            original = Servico.objects.get(id=self.id)

        if self.id is None:
            # Novo serviço, email de ativação
            subject = u'INTERLEGIS - Ativação de serviço %s' % (self.tipo_servico.nome,)
            body = self.tipo_servico.template_email_ativa
        elif self.data_desativacao is not None and original.data_desativacao is None:
            # Serviço foi desativado. Email de desativação
            subject = u'INTERLEGIS - Desativação de serviço %s' % (self.tipo_servico.nome,)
            body = self.tipo_servico.template_email_desativa
        elif (self.tipo_servico != original.tipo_servico or
              self.contato_tecnico != original.contato_tecnico or
              self.url != original.url or
              self.nome_servidor != original.nome_servidor or
              self.senha_inicial != original.senha_inicial):
            # Serviço foi alterado
            subject = u'INTERLEGIS - Alteração de serviço %s' % (self.tipo_servico.nome,)
            body = self.tipo_servico.template_email_altera
        else:
            # Salvar o Servico
            super(Servico, self).save(*args, **kwargs)
            return # sem enviar email
        
        # Prepara e envia o email
        body = body.replace('{url}', self.url) \
            .replace('{senha}', self.senha_inicial) \
            .replace('{motivo}', self.motivo_desativacao)
            
#        send_mail(subject, body, DEFAULT_FROM_EMAIL, \
#                  (self.contato_tecnico.email,), fail_silently=False)
        
        # Salvar o Servico
        super(Servico, self).save(*args, **kwargs)

        return
    
class LogServico(models.Model):
    servico = models.ForeignKey(Servico, verbose_name='Serviço')
    descricao = models.CharField('Breve descrição da ação', max_length=60)
    data = models.DateField('Data da ação', default=date.today)
    log = models.TextField('Log da ação')
    
    def __unicode__(self):
        return "%s (%s)" % (self.descricao, self.data)
    
    class Meta:
        verbose_name = 'Log do serviço'
        verbose_name_plural = 'Logs do serviço'    

class CasaAtendidaManager(models.Manager):
    def get_query_set(self):
        qs = super(CasaAtendidaManager, self).get_query_set()
        qs = qs.exclude(codigo_interlegis='')
        return qs

class CasaAtendida(CasaLegislativa):
    class Meta:
        proxy = True
        verbose_name_plural = 'Casas atendidas'

    objects =  CasaAtendidaManager()
    
    @property        
    def servicos(self):
        result = []
        for servico in self.servico_set.all():
            result.append(unicode(servico))
            
        return ", ".join(result)