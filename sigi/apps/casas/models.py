# -*- coding: utf-8 -*-
import random
from datetime import datetime
from string import ascii_uppercase
from unicodedata import normalize

from django.contrib.contenttypes import fields
from django.db import models
from image_cropping import ImageRatioField

from sigi.apps.servidores.models import Servidor
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
    
    INCLUSAO_DIGITAL_CHOICES = (
        ('NAO PESQUISADO', u'Não pesquisado'),
        ('NAO POSSUI PORTAL', u'Não possui portal'),
        ('PORTAL MODELO', u'Possui Portal Modelo'),
        ('OUTRO PORTAL', u'Possui outro portal'),
    )
    
    nome = models.CharField(
        max_length=60,
        help_text='Exemplo: <em>Câmara Municipal de Pains</em>.'
    )

    # Guarda um campo para ser usado em buscas em caixa baixa e sem acento
    search_text = SearchField(field_names=['nome'])
    # search_text.projeto_filter = True
    tipo = models.ForeignKey(TipoCasaLegislativa, verbose_name="Tipo")
    cnpj = models.CharField('CNPJ', max_length=32, blank=True)
    observacoes = models.TextField(u'observações', blank=True)
#    num_parlamentares = models.PositiveIntegerField('Número de parlamentares')
    codigo_interlegis = models.CharField('Código Interlegis', max_length=3, blank=True)
    # codigo_interlegis.ts_filter = True

    gerente_contas = models.ForeignKey(Servidor, verbose_name="Gerente de contas", null=True, blank=True, related_name='casas_que_gerencia')

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
    # municipio.uf_filter = True

    cep = models.CharField(max_length=32)
    email = models.EmailField('e-mail', max_length=128, blank=True)
    pagina_web = models.URLField(
        u'página web',
        help_text='Exemplo: <em>http://www.camarapains.mg.gov.br</em>.',
        blank=True,
    )
    inclusao_digital = models.CharField(max_length=30, choices=INCLUSAO_DIGITAL_CHOICES, default=INCLUSAO_DIGITAL_CHOICES[0][0])
    data_levantamento = models.DateTimeField(u"Data/hora da pesquisa", null=True, blank=True)
    pesquisador = models.ForeignKey(Servidor, verbose_name=u"Pesquisador", null=True, blank=True)
    obs_pesquisa = models.TextField(u"Observações do pesquisador", blank=True)
    ult_alt_endereco = models.DateTimeField(u'Última alteração do endereço', null=True, blank=True, editable=True)
    telefones = fields.GenericRelation('contatos.Telefone')

    foto = models.ImageField(
        upload_to='imagens/casas',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    recorte = ImageRatioField('foto', '400x300', verbose_name="Recorte", )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    data_instalacao = models.DateField(u'Data de instalação da Casa Legislativa', null=True, blank=True)

    class Meta:
        ordering = ('nome',)
        unique_together = ('municipio', 'tipo')
        verbose_name = 'Casa Legislativa'
        verbose_name_plural = 'Casas Legislativas'

    @property
    def num_parlamentares(self):
        if not self.legislatura_set.exists():
            return 0
        return self.legislatura_set.latest('data_inicio').total_parlamentares

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
            if self.funcionario_set.filter(setor='presidente').count() > 1:
                return self.funcionario_set.filter(setor='presidente')[0]
            else:
                return self.funcionario_set.get(setor='presidente')
        except Funcionario.DoesNotExist:
            return None

    @property
    def total_parlamentares(self):
        """
        Calcula o total de parlamentares atual da Casa:
        - O total de parlamentares da legislatura mais recente, ou
        - num_parlamentares ou
        - 0 se não tiver nenhuma das informações
        """

        if self.legislatura_set.exists():
            return self.legislatura_set.all()[0].total_parlamentares

        if self.num_parlamentares is not None:
            return self.num_parlamentares

        return 0

    def gerarCodigoInterlegis(self):
        codigo = self.codigo_interlegis

        if codigo == '':
            if self.tipo.sigla == 'AL':  # Assembléias são tratadas a parte
                codigo = 'A' + self.municipio.uf.sigla
                if CasaLegislativa.objects.filter(codigo_interlegis=codigo).count() <= 0:
                    # Só grava o código se ele for inédito
                    self.codigo_interlegis = codigo
                    self.save()
                    return codigo
                # Se já existe, então trata a Assembleia como uma Casa qualquer.

            cityName = normalize('NFKD', unicode(self.municipio.nome)).encode('ascii', 'ignore')
            cityName = cityName.upper().strip()
            cityName = cityName.replace(' DA ', ' ')
            cityName = cityName.replace(' DE ', ' ')
            cityName = cityName.replace(' DO ', ' ')
            cityName = filter(lambda x: x in ascii_uppercase + ' ', cityName)

            # estratégia 1 - Pegar as 1ª letra de cada nome da cidade
            codigo = ''.join([x[0] for x in cityName.split(' ')[:3]])

            # Se o código ficou com menos que três letras, pegar as 2 primeiras
            if len(codigo) < 3:
                codigo = ''.join([x[0:2] for x in cityName.split(' ')[:3]])[:3]

            # Se ainda ficou com menos de três letras, então o nome da cidade só
            # tem uma palavra. Pegue as três primeiras letras da palavra
            if len(codigo) < 3:
                codigo = cityName[:3]

            # Se o código já existir, substituir a última letra do código pela
            # última letra do nome da cidade, e ir recuando, letra a letra,
            # até achar um novo código.

            cityName = cityName.replace(' ', '')
            ultima = len(cityName)

            while CasaLegislativa.objects.filter(codigo_interlegis=codigo). \
                    count() > 0 and ultima > 0:
                codigo = codigo[:2] + cityName[ultima - 1: ultima]
                ultima -= 1

            # Se usou todas as letras do nome na última posição e ainda assim
            # não gerou um código único, então vamos compor o nome usando as
            # três primeiras consoantes.

            if CasaLegislativa.objects.filter(codigo_interlegis=codigo).count() > 0:
                codigo_cons = cityName.replace('A', '').replace('E', '').\
                    replace('I', '').replace('O', '').replace('U', '')[:3]
                if len(codigo_cons) == 3 and \
                        CasaLegislativa.objects.filter(codigo_interlegis=codigo).count() > 0:
                    codigo = codigo_cons

            # Se ainda não gerou um nome único, vamos colocar dígitos no
            # último caractere, de A a Z

            i = 'A'

            while CasaLegislativa.objects.filter(codigo_interlegis=codigo). \
                    count() > 0 and i <= 'Z':
                codigo = codigo[:2] + str(i)
                i = chr(ord(i) + 1)

            # Se não encontrou, comece a gerar strings com 3 letras aleatórias
            # tiradas do nome da cidade, até gerar uma que não existe. Tentar
            # 100 vezes apenas

            i = 0

            while CasaLegislativa.objects.filter(codigo_interlegis=codigo). \
                    count() > 0 and i < 100:
                codigo = random.choice(cityName) + random.choice(cityName) + \
                    random.choice(cityName)
                i += 1

            # Caramba! Só resta então gerar o código com 3 letras aleatórias
            # quaisquer do alfabeto!

            i = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

            while CasaLegislativa.objects.filter(codigo_interlegis=codigo). \
                    count() > 0:
                codigo = random.choice(i) + random.choice(i) + \
                    random.choice(i)

            self.codigo_interlegis = codigo
            self.save()

        return codigo

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        address_changed = False

        if self.pk is not None:
            original = CasaLegislativa.objects.get(pk=self.pk)
            if (self.logradouro != original.logradouro or
                    self.bairro != original.bairro or
                    self.municipio != original.municipio or
                    self.cep != original.cep):
                address_changed = True
        else:
            address_changed = True

        if address_changed:
            self.ult_alt_endereco = datetime.now()

        return super(CasaLegislativa, self).save(*args, **kwargs)


class Funcionario(models.Model):

    """ Modelo para registrar contatos vinculados às
    Casas Legislativas
    """

    SETOR_CHOICES = [
        ("presidente", "Presidente"),
        ("contato_interlegis", "Contato Interlegis"),
        ("infraestrutura_fisica", "Infraestrutura Física"),
        ("estrutura_de_ti", "Estrutura de TI"),
        ("organizacao_do_processo_legislativo", "Organização do Processo Legislativo"),
        ("producao_legislativa", "Produção Legislativa"),
        ("estrutura_de_comunicacao_social", "Estrutura de Comunicação Social"),
        ("estrutura_de_recursos_humanos", "Estrutura de Recursos Humanos"),
        ("gestao", "Gestão"),
        ("outros", "Outros"),
    ]
    SEXO_CHOICES = [
        ("M", "Masculino"),
        ("F", "Feminino")
    ]

    casa_legislativa = models.ForeignKey(CasaLegislativa)
    nome = models.CharField('nome completo', max_length=60, blank=False)
    # nome.alphabetic_filter = True
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default="M")
    nota = models.CharField(max_length=70, null=True, blank=True)
    email = models.CharField('e-mail', max_length=75, blank=True)
    telefones = fields.GenericRelation('contatos.Telefone')
    endereco = fields.GenericRelation('contatos.Endereco')
    cargo = models.CharField(max_length=100, null=True, blank=True)
    funcao = models.CharField(u'função', max_length=100, null=True, blank=True)
    setor = models.CharField(max_length=100, choices=SETOR_CHOICES, default="outros")
    tempo_de_servico = models.CharField(u'tempo de serviço', max_length=50, null=True, blank=True)
    ult_alteracao = models.DateTimeField(u'Última alteração', null=True, blank=True, editable=True, auto_now=True)

    class Meta:
        ordering = ('nome',)
        verbose_name = 'contato da Casa Legislativa'
        verbose_name_plural = 'contatos da Casa Legislativa'

    def __unicode__(self):
        return self.nome


class PresidenteManager(models.Manager):

    def get_queryset(self):
        qs = super(PresidenteManager, self).get_queryset()
        qs = qs.filter(setor='presidente')
        return qs


class Presidente(Funcionario):

    class Meta:
        proxy = True

    objects = PresidenteManager()

    def save(self, *args, **kwargs):
        self.setor = 'presidente'
        self.cargo = 'Presidente'
        self.funcao = 'Presidente'
        return super(Presidente, self).save(*args, **kwargs)
