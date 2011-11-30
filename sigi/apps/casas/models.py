# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.utils import SearchField

class TipoCasaLegislativa(models.Model):
    """ Modelo para representar o tipo da Casa Legislativa

    Geralmente: Câmara Municipal, Assembléia Legislativa,
    Câmara Distrital ou Legislativo Federal
    """

    sigla = models.CharField(
        max_length=5
    )
    nome = models.CharField(
        max_length=100
    )
    def __unicode__(self):
        return self.nome


class CasaLegislativa(models.Model):
    """ Modelo para representar uma Casa Legislativa
    """
    nome = models.CharField(
        max_length=60,
        help_text='Exemplo: <em>Câmara Municipal de Pains</em>.'
    )

    # Guarda um campo para ser usado em buscas em caixa baixa e sem acento
    search_text = SearchField(field_names=['nome'])
    tipo = models.ForeignKey(TipoCasaLegislativa, verbose_name="Tipo")
    cnpj = models.CharField('CNPJ', max_length=32, blank=True)
    observacoes = models.TextField(u'observações', blank=True)

    # Informações de contato
    logradouro = models.CharField(
        max_length=100,
        help_text='Avenida, rua, praça, jardim, parque...'
    )
    bairro = models.CharField(max_length=100, blank=True)
    municipio = models.ForeignKey(
        'contatos.Municipio',
        verbose_name='município'
    )
    municipio.uf_filter = True
    cep = models.CharField(max_length=32)
    email = models.EmailField('e-mail', max_length=128, blank=True)
    pagina_web = models.URLField(
        u'página web',
        help_text='Exemplo: <em>http://www.camarapains.mg.gov.br</em>.',
        blank=True,
        verify_exists=False
    )
    telefones = generic.GenericRelation('contatos.Telefone')

    foto = models.ImageField(
        upload_to='imagens/casas',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)


    class Meta:
        ordering = ('nome',)
        unique_together = ('municipio', 'tipo')
        verbose_name = 'Casa Legislativa'
        verbose_name_plural = 'Casas Legislativas'

    def __unicode__(self):
        return self.nome

class Funcionario(models.Model):
    """ Modelo para registrar contatos vinculados às
    Casas Legislativas
    """
    SETOR_CHOICES = [
        ("presidencia","Presidencia"),
        ("infraestrutura_fisica","Infraestrutura Física"),
        ("estrutura_de_ti","Estrutura de TI"),
        ("organizacao_do_processo_legislativo","Organização do Processo Legislativo"),
        ("estrutura_de_comunicacao_social","Estrutura de Comunicação Social"),
        ("estrutura_de_recursos_humanos","Estrutura de Recursos Humanos"),
        ("estrutura_de_recursos_humanos","Estrutura de Recursos Humanos"),
        ("estrutura_de_secretaria","Estrutura de Secretaria"),
        ("outros","Outros"),
        ]
    casa_legislativa = models.ForeignKey(CasaLegislativa)
    nome = models.CharField('nome completo', max_length=60)
    nome.alphabetic_filter = True
    nota = models.CharField(max_length=70, blank=True)
    email = models.EmailField('e-mail', blank=True)
    telefones = generic.GenericRelation('contatos.Telefone')
    endereco = generic.GenericRelation('contatos.Endereco')
    cargo = models.CharField(max_length=100, null=True, blank=True)
    funcao = models.CharField(u'função', max_length=100, null=True, blank=True)
    setor = models.CharField(max_length=100, choices = SETOR_CHOICES, default="outros")
    tempo_de_servico = models.CharField(u'tempo de serviço', max_length=50, null=True, blank=True)

    class Meta:
        ordering = ('nome',)
        verbose_name = 'contato Casa Legislativa'
        verbose_name_plural = 'contatos Casas Legislativa'

    def __unicode__(self):
        return self.nome

class PresidenteManager(models.Manager):
    def get_query_set(self):
        qs = super(PresidenteManager, self).get_query_set()
        qs = qs.filter(cargo='Presidente')
        return qs

class Presidente(Funcionario):
    class Meta:
        proxy = True

    objects =  PresidenteManager()

    def save(self, *args, **kwargs):
        self.cargo = 'Presidente'
        self.setor = 'presidencia'
        return super(Presidente, self).save(*args, **kwargs)
