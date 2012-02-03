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

    @property
    def telefone(self):
        """ Link para acessar diretamente o primeiro telefone cadastrado da casa
            Util para relatorios antigos
        """
        telefones = self.telefones.all()
        if telefones:
            return telefones[0]
        return None

    @property
    def presidente(self):
        """ Link para acessar diretamente o contato do presidente da casa
            Util para relatorios antigos
        """
        try:
            return self.funcionario_set.get(setor='presidente')
        except Funcionario.DoesNotExist:
            return None

    def __unicode__(self):
        return self.nome

class Funcionario(models.Model):
    """ Modelo para registrar contatos vinculados às
    Casas Legislativas
    """
    SETOR_CHOICES = [
        ("presidente","Presidente"),
        ("contato_interlegis","Contato Interlegis"),
        ("infraestrutura_fisica","Infraestrutura Física"),
        ("estrutura_de_ti","Estrutura de TI"),
        ("organizacao_do_processo_legislativo","Organização do Processo Legislativo"),
        ("producao_legislativa","Produção Legislativa"),
        ("estrutura_de_comunicacao_social","Estrutura de Comunicação Social"),
        ("estrutura_de_recursos_humanos","Estrutura de Recursos Humanos"),
        ("gestao","Gestão"),
        ("outros","Outros"),
        ]
    casa_legislativa = models.ForeignKey(CasaLegislativa)
    nome = models.CharField('nome completo', max_length=60, blank=True)
    nome.alphabetic_filter = True
    nota = models.CharField(max_length=70, null=True, blank=True)
    email = models.EmailField('e-mail', null=True, blank=True)
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
        qs = qs.filter(setor='presidente')
        return qs

class Presidente(Funcionario):
    class Meta:
        proxy = True

    objects =  PresidenteManager()

    def save(self, *args, **kwargs):
        self.setor = 'presidente'
        self.cargo = 'Presidente'
        self.funcao = 'Presidente'
        return super(Presidente, self).save(*args, **kwargs)

