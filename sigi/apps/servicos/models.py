# -*- coding: utf-8 -*-
from django.db import models
from sigi.apps.casas.models import CasaLegislativa, Funcionario
from datetime import date
from django.core.mail import send_mail
from sigi.settings import DEFAULT_FROM_EMAIL


class TipoServico(models.Model):
    email_help = u'''Use:<br/>
                        {url} para incluir a URL do serviço,<br/>
                        {senha} para incluir a senha inicial do serviço'''
    nome = models.CharField(u'Nome', max_length=60)
    sigla = models.CharField(u'Sigla', max_length='12')
    string_pesquisa = models.CharField(u'String de pesquisa', blank=True, max_length=200,
                                       help_text=u'Sufixo para pesquisa RSS para averiguar a data da última atualização do serviço')
    template_email_ativa = models.TextField(u'Template de email de ativação', help_text=email_help, blank=True)
    template_email_altera = models.TextField(u'Template de email de alteração', help_text=email_help, blank=True)
    template_email_desativa = models.TextField(u'Template de email de desativação', help_text=email_help + u'<br/>{motivo} para incluir o motivo da desativação do serviço', blank=True)

    @property
    def qtde_casas_atendidas(self):
        u"""Quantidade de casas atendidas"""
        return self.servico_set.filter(data_desativacao=None).count()

    class Meta:
        verbose_name = u'Tipo de serviço'
        verbose_name_plural = u'Tipos de serviço'

    def __unicode__(self):
        return self.nome


class Servico(models.Model):
    casa_legislativa = models.ForeignKey(CasaLegislativa, verbose_name=u'Casa Legislativa')
    tipo_servico = models.ForeignKey(TipoServico, verbose_name=u'Tipo de serviço')
    contato_tecnico = models.ForeignKey(Funcionario, verbose_name=u'Contato técnico', related_name='contato_tecnico')
    contato_administrativo = models.ForeignKey(Funcionario, verbose_name=u'Contato administrativo', related_name='contato_administrativo')
    url = models.URLField(u'URL do serviço', blank=True)
    hospedagem_interlegis = models.BooleanField(u'Hospedagem no Interlegis?')
    nome_servidor = models.CharField(u'Hospedado em', max_length=60, blank=True,
                                     help_text=u'Se hospedado no Interlegis, informe o nome do servidor.<br/>Senão, informe o nome do provedor de serviços.')
    porta_servico = models.PositiveSmallIntegerField(u'Porta de serviço (instância)', blank=True, null=True)
    senha_inicial = models.CharField(u'Senha inicial', max_length=33, blank=True)
    data_ativacao = models.DateField(u'Data de ativação', default=date.today)
    data_alteracao = models.DateField(u'Data da última alteração', blank=True, null=True, auto_now=True)
    data_desativacao = models.DateField(u'Data de desativação', blank=True, null=True)
    motivo_desativacao = models.TextField(u'Motivo da desativação', blank=True)
    data_ultimo_uso = models.DateField(u'Data da última utilização', blank=True, null=True,
                                       help_text=u'Data em que o serviço foi utilizado pela Casa Legislativa pela última vez<br/><strong>NÃO É ATUALIZADO AUTOMATICAMENTE!</strong>')
    erro_atualizacao = models.CharField(u"Erro na atualização", blank=True, max_length=200,
                                        help_text=u"Erro ocorrido na última tentativa de atualizar a data de último acesso")

    # casa_legislativa.casa_uf_filter = True

    def atualiza_data_uso(self):
        def reset(erro=u"", comment=u""):
            if self.data_ultimo_uso is None and not erro:
                return
            self.data_ultimo_uso = None
            self.erro_atualizacao = comment + '<br/>' + erro
            self.save()
            return

        if self.tipo_servico.string_pesquisa == "":
            reset()
            return

        url = self.url

        if not url:
            reset()
            return

        if url[-1] != '/':
            url += '/'
        url += self.tipo_servico.string_pesquisa

        import urllib2
        from xml.dom.minidom import parseString

        try:  # Captura erros de conexão
            try:  # Tentar conxão sem proxy
                req = urllib2.urlopen(url=url, timeout=5)
            except:  # Tentar com proxy
                proxy = urllib2.ProxyHandler()
                opener = urllib2.build_opener(proxy)
                req = opener.open(fullurl=url, timeout=5)
        except Exception as e:
            reset(erro=str(e), comment=u'Não foi possível conectar com o servidor. Pode estar fora do ar ou não ser um ' +
                  self.tipo_servico.nome)
            return

        try:
            rss = req.read()
        except Exception as e:
            reset(erro=str(e), comment=u'Não foi possível receber os dados do servidor. O acesso pode ter sido negado.')
            return

        try:
            xml = parseString(rss)
            items = xml.getElementsByTagName('item')
            first_item = items[0]
            date_list = first_item.getElementsByTagName('dc:date')
            date_item = date_list[0]
            date_text = date_item.firstChild.nodeValue
            self.data_ultimo_uso = date_text[:10]  # Apenas YYYY-MM-DD
            self.erro_atualizacao = ""
            self.save()
        except Exception as e:
            reset(erro=str(e), comment=u'A resposta do servidor não é compatível com %s. Pode ser outro software que está sendo usado' %
                  self.tipo_servico.nome)
        return

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
            return  # sem enviar email

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

    def get_queryset(self):
        qs = super(CasaAtendidaManager, self).get_queryset()
        qs = qs.exclude(codigo_interlegis='')
        return qs


class CasaAtendida(CasaLegislativa):

    class Meta:
        proxy = True
        verbose_name_plural = 'Casas atendidas'

    objects = CasaAtendidaManager()


class CasaManifesta(models.Model):
    casa_legislativa = models.OneToOneField(CasaLegislativa)
    data_manifestacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    informante = models.CharField(u'Nome do informante', max_length=100, blank=True)
    cargo = models.CharField(u'Cargo do informante', max_length=100, blank=True)
    email = models.EmailField(u'E-mail de contato', blank=True)


class ServicoManifesto(models.Model):
    casa_manifesta = models.ForeignKey(CasaManifesta)
    servico = models.ForeignKey(TipoServico)
    url = models.URLField(blank=True)
    hospedagem_interlegis = models.BooleanField(u'Hospedagem no Interlegis?')

    class Meta:
        unique_together = ('casa_manifesta', 'servico')


class RegistroServico(models.Model):
    produto = models.CharField(max_length=50)
    versao = models.CharField(max_length=30)
    url = models.URLField()
    data_registro = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = u'Registro de serviços'
