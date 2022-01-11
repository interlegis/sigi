from datetime import datetime
import random
from string import ascii_uppercase
from unicodedata import normalize
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from sigi.apps.contatos.models import Municipio
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils import SearchField

class TipoOrgao(models.Model):
    sigla = models.CharField(_("Sigla"), max_length=5)
    nome = models.CharField(_("Nome"), max_length=100)
    legislativo = models.BooleanField(_("Poder legislativo"), default=False)

    class Meta:
        ordering = ('nome',)
        verbose_name = _("Tipo de órgão")
        verbose_name_plural = _("Tipos de órgão")

    def __str__(self):
        return self.nome

class Orgao(models.Model):
    INCLUSAO_DIGITAL_CHOICES = (
        ('NAO PESQUISADO', _('Não pesquisado')),
        ('NAO POSSUI PORTAL', _('Não possui portal')),
        ('PORTAL MODELO', _('Possui Portal Modelo')),
        ('OUTRO PORTAL', _('Possui outro portal')),
    )

    nome = models.CharField(
        _("nome"),
        max_length=60,
        help_text=_('Exemplo: <em>Câmara Municipal de Pains</em>.')
    )
    sigla = models.CharField(
        _("sigla do órgão"),
        max_length=30,
        blank=True
    )
    # Guarda um campo para ser usado em buscas em caixa baixa e sem acento
    search_text = SearchField(field_names=['nome'])
    tipo = models.ForeignKey(
        TipoOrgao,
        on_delete=models.PROTECT,
        verbose_name=_("tipo")
    )
    cnpj = models.CharField(_("CNPJ"), max_length=32, blank=True)
    observacoes = models.TextField(_('observações'), blank=True)
    horario_funcionamento = models.CharField(
        _("horário de funcionamento da Casa Legislativa"),
        max_length=100,
        blank=True,
    )
    codigo_interlegis = models.CharField(
        _('código Interlegis'),
        max_length=3,
        blank=True
    )
    gerentes_interlegis = models.ManyToManyField(
        Servidor,
        verbose_name=_("Gerentes Interlegis"),
        related_name='casas_que_gerencia',
        blank=True,
    )
    # Informações de contato
    logradouro = models.CharField(
        _("logradouro"),
        max_length=100,
        help_text=_('Avenida, rua, praça, jardim, parque...')
    )
    bairro = models.CharField(_("bairro"), max_length=100, blank=True)
    municipio = models.ForeignKey(
        'contatos.Municipio',
        on_delete=models.PROTECT,
        verbose_name=_('município')
    )
    cep = models.CharField(_("CEP"), max_length=32)
    email = models.EmailField(_('e-mail'), max_length=128, blank=True)
    pagina_web = models.URLField(
        _('página web'),
        help_text=_('Exemplo: <em>http://www.camarapains.mg.gov.br</em>.'),
        blank=True,
    )
    inclusao_digital = models.CharField(
        _("inclusão digital"),
        max_length=30,
        choices=INCLUSAO_DIGITAL_CHOICES,
        default=INCLUSAO_DIGITAL_CHOICES[0][0]
    )
    data_levantamento = models.DateTimeField(
        _("data/hora da pesquisa"),
        null=True,
        blank=True
    )
    pesquisador = models.ForeignKey(
        Servidor,
        on_delete=models.SET_NULL,
        verbose_name=_("pesquisador"),
        null=True,
        blank=True
    )
    obs_pesquisa = models.TextField(
        _("observações do pesquisador"),
        blank=True
    )
    ult_alt_endereco = models.DateTimeField(
        _('última alteração do endereço'),
        null=True,
        blank=True,
        editable=True
    )
    telefones = GenericRelation('contatos.Telefone')
    foto = models.ImageField(
        _("foto"),
        upload_to='imagens/casas',
        width_field='foto_largura',
        height_field='foto_altura',
        blank=True
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    data_instalacao = models.DateField(
        _('data de instalação da Casa Legislativa'),
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('nome',)
        verbose_name = _('órgão')
        verbose_name_plural = _('órgãos')

    def lista_gerentes(self, fmt='html'):
        if not self.gerentes_interlegis.exists():
            return ""
        if fmt == 'html':
            return "<ul><li>"+"</li><li>".join(
                [g.nome_completo for g in self.gerentes_interlegis.all()])+\
                "</li></ul>"
        else:
            return ", ".join([g.nome_completo for g in
                               self.gerentes_interlegis.all()])

    @property
    def num_parlamentares(self):
        # TODO: Descomentar assim que a app Parlamentares for migrada
        # if not self.legislatura_set.exists():
        #     return 0
        # return self.legislatura_set.latest('data_inicio').total_parlamentares
        return 0

    @property
    def telefone(self):
        telefones = self.telefones.all()
        if telefones:
            return telefones[0]
        return None

    @property
    def presidente(self):
        try:
            if self.funcionario_set.filter(setor='presidente').count() > 1:
                return self.funcionario_set.filter(setor='presidente')[0]
            else:
                return self.funcionario_set.get(setor='presidente')
        except Funcionario.DoesNotExist:
            return None

    @property
    def contato_interlegis(self):
        try:
            if self.funcionario_set.filter(setor='contato_interlegis').count() > 1:
                return self.funcionario_set.filter(setor='contato_interlegis')[0]
            else:
                return self.funcionario_set.get(setor='contato_interlegis')
        except Funcionario.DoesNotExist:
            return None

    def gerarCodigoInterlegis(self):
        codigo = self.codigo_interlegis

        if codigo == '':
            if self.tipo.sigla == 'AL':  # Assembléias são tratadas a parte
                codigo = 'A' + self.municipio.uf.sigla
                if Orgao.objects.filter(codigo_interlegis=codigo).count() <= 0:
                    # Só grava o código se ele for inédito
                    self.codigo_interlegis = codigo
                    self.save()
                    return codigo
                # Se já existe, então trata a Assembleia como uma Casa qualquer.

            cityName = normalize('NFKD', self.municipio.nome).encode(
                'ascii', 'ignore')
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

            while Orgao.objects.filter(codigo_interlegis=codigo). \
                    count() > 0 and ultima > 0:
                codigo = codigo[:2] + cityName[ultima - 1: ultima]
                ultima -= 1

            # Se usou todas as letras do nome na última posição e ainda assim
            # não gerou um código único, então vamos compor o nome usando as
            # três primeiras consoantes.

            if Orgao.objects.filter(codigo_interlegis=codigo).count() > 0:
                codigo_cons = cityName.replace('A', '').replace('E', '').\
                    replace('I', '').replace('O', '').replace('', '')[:3]
                if len(codigo_cons) == 3 and \
                        Orgao.objects.filter(codigo_interlegis=codigo).count() > 0:
                    codigo = codigo_cons

            # Se ainda não gerou um nome único, vamos colocar dígitos no
            # último caractere, de A a Z

            i = 'A'

            while Orgao.objects.filter(codigo_interlegis=codigo). \
                    count() > 0 and i <= 'Z':
                codigo = codigo[:2] + str(i)
                i = chr(ord(i) + 1)

            # Se não encontrou, comece a gerar strings com 3 letras aleatórias
            # tiradas do nome da cidade, até gerar uma que não existe. Tentar
            # 100 vezes apenas

            i = 0

            while Orgao.objects.filter(codigo_interlegis=codigo). \
                    count() > 0 and i < 100:
                codigo = random.choice(cityName) + random.choice(cityName) + \
                    random.choice(cityName)
                i += 1

            # Caramba! Só resta então gerar o código com 3 letras aleatórias
            # quaisquer do alfabeto!

            i = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

            while Orgao.objects.filter(codigo_interlegis=codigo).count() > 0:
                codigo = random.choice(i) + random.choice(i) + random.choice(i)

            self.codigo_interlegis = codigo
            self.save()

        return codigo

    def __str__(self):
        return self.nome

    def clean(self):
        if (hasattr(self, 'tipo') and hasattr(self, 'municipio')
            and self.tipo.legislativo):
            if Orgao.objects.filter(
                tipo=self.tipo,
                municipio=self.municipio).exclude(pk=self.pk).exists():
                raise ValidationError(
                    _("Já existe um(a) %(tipo)s em %(municipio)s"),
                    code='integrity',
                    params={'tipo': self.tipo, 'municipio': self.municipio})

    def save(self, *args, **kwargs):
        address_changed = False

        if self.pk is not None:
            original = Orgao.objects.get(pk=self.pk)
            if (self.logradouro != original.logradouro or
                    self.bairro != original.bairro or
                    self.municipio != original.municipio or
                    self.cep != original.cep):
                address_changed = True
        else:
            address_changed = True

        if address_changed:
            self.ult_alt_endereco = datetime.now()

        return super(Orgao, self).save(*args, **kwargs)

class Funcionario(models.Model):
    SETOR_CHOICES = [
        ("presidente", _("Presidente")),
        ("contato_interlegis", _("Contato Interlegis")),
        ("infraestrutura_fisica", _("Infraestrutura Física")),
        ("estrutura_de_ti", _("Estrutura de TI")),
        ("organizacao_do_processo_legislativo",
         _("Organização do Processo Legislativo")),
        ("producao_legislativa", _("Produção Legislativa")),
        ("estrutura_de_comunicacao_social",
         _("Estrutura de Comunicação Social")),
        ("estrutura_de_recursos_humanos", _("Estrutura de Recursos Humanos")),
        ("gestao", _("Gestão")),
        ("outros", _("Outros")),
    ]
    SEXO_CHOICES = [
        ("M", _("Masculino")),
        ("F", _("Feminino"))
    ]

    casa_legislativa = models.ForeignKey(
        Orgao,
        on_delete=models.CASCADE,
        verbose_name=_("órgão"),
    )
    nome = models.CharField(_('nome completo'), max_length=60, blank=False)
    sexo = models.CharField(
        _("sexo"),
        max_length=1,
        choices=SEXO_CHOICES,
        default="M"
    )
    data_nascimento = models.DateField(
        _("data de nascimento"),
        blank=True,
        null=True
    )
    nota = models.CharField(
        _("telefones"),
        max_length=250,
        null=True,
        blank=True
    )
    email = models.CharField(_('e-mail'), max_length=250, blank=True)
    endereco = models.CharField(_('endereço'), max_length=100, blank=True)
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        verbose_name=_('municipio'),
        null=True,
        blank=True,
    )
    bairro = models.CharField(_('bairro'), max_length=100, blank=True)
    cep = models.CharField(_('CEP'), max_length=10, blank=True)
    redes_sociais = models.TextField(
        _('redes sociais'),
        help_text=_('Colocar um por linha'),
        blank=True
    )
    cargo = models.CharField(_("cargo"), max_length=100, null=True, blank=True)
    funcao = models.CharField(
        _('função'),
        max_length=100,
        null=True,
        blank=True
    )
    setor = models.CharField(
        _("setor"),
        max_length=100,
        choices=SETOR_CHOICES,
        default="outros"
    )
    tempo_de_servico = models.CharField(
        _('tempo de serviço'),
        max_length=50,
        null=True,
        blank=True
    )
    ult_alteracao = models.DateTimeField(
        _('última alteração'),
        null=True,
        blank=True,
        editable=True,
        auto_now=True
    )
    desativado = models.BooleanField(_("desativado"), default=False)
    observacoes = models.TextField(_("observações"), blank=True)

    class Meta:
        ordering = ('nome',)
        verbose_name = _('contato da Casa Legislativa')
        verbose_name_plural = _('contatos da Casa Legislativa')

    def __str__(self):
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