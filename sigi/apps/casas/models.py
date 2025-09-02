import random
from difflib import SequenceMatcher
from string import ascii_uppercase
from unicodedata import normalize
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from sigi.apps.contatos.models import Municipio
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils import SearchField, mask_cnpj, valida_cnpj, to_ascii


class TipoOrgao(models.Model):
    sigla = models.CharField(_("Sigla"), max_length=5)
    nome = models.CharField(_("Nome"), max_length=100)
    legislativo = models.BooleanField(_("Poder legislativo"), default=False)

    class Meta:
        ordering = ("nome",)
        verbose_name = _("Tipo de órgão")
        verbose_name_plural = _("Tipos de órgão")

    def __str__(self):
        return self.nome


class Orgao(models.Model):
    INCLUSAO_DIGITAL_CHOICES = (
        ("NAO PESQUISADO", _("Não pesquisado")),
        ("NAO POSSUI PORTAL", _("Não possui portal")),
        ("PORTAL MODELO", _("Possui Portal Modelo")),
        ("OUTRO PORTAL", _("Possui outro portal")),
    )

    nome = models.CharField(
        _("nome"),
        max_length=60,
        help_text=_("Exemplo: <em>Câmara Municipal de Pains</em>."),
    )
    sigla = models.CharField(_("sigla do órgão"), max_length=30, blank=True)
    # Guarda um campo para ser usado em buscas em caixa baixa e sem acento
    search_text = SearchField(field_names=["nome"])
    tipo = models.ForeignKey(
        TipoOrgao, on_delete=models.PROTECT, verbose_name=_("tipo")
    )
    cnpj = models.CharField(_("CNPJ"), max_length=32, blank=True)
    observacoes = models.TextField(_("observações"), blank=True)
    horario_funcionamento = models.CharField(
        _("horário de funcionamento da Casa Legislativa"),
        max_length=100,
        blank=True,
    )
    codigo_interlegis = models.CharField(
        _("código Interlegis"), max_length=3, blank=True
    )
    gerentes_interlegis = models.ManyToManyField(
        Servidor,
        verbose_name=_("Gerentes Interlegis"),
        related_name="casas_que_gerencia",
        blank=True,
    )
    # Informações de contato
    logradouro = models.CharField(
        _("logradouro"),
        max_length=100,
        help_text=_("Avenida, rua, praça, jardim, parque..."),
    )
    bairro = models.CharField(_("bairro"), max_length=100, blank=True)
    municipio = models.ForeignKey(
        "contatos.Municipio",
        on_delete=models.PROTECT,
        verbose_name=_("município"),
    )
    cep = models.CharField(_("CEP"), max_length=32)
    email = models.EmailField(_("email"), max_length=128, blank=True)
    pagina_web = models.URLField(
        _("página web"),
        help_text=_("Exemplo: <em>http://www.camarapains.mg.gov.br</em>."),
        blank=True,
    )
    inclusao_digital = models.CharField(
        _("inclusão digital"),
        max_length=30,
        choices=INCLUSAO_DIGITAL_CHOICES,
        default=INCLUSAO_DIGITAL_CHOICES[0][0],
    )
    data_levantamento = models.DateTimeField(
        _("data/hora da pesquisa"), null=True, blank=True
    )
    pesquisador = models.ForeignKey(
        Servidor,
        on_delete=models.SET_NULL,
        verbose_name=_("pesquisador"),
        null=True,
        blank=True,
    )
    obs_pesquisa = models.TextField(
        _("observações do pesquisador"), blank=True
    )
    ult_alt_endereco = models.DateTimeField(
        _("última alteração do endereço"), null=True, blank=True, editable=True
    )
    telefone_geral = models.CharField(
        _("telefone geral"),
        max_length=64,
        blank=True,
        default="",
        help_text=_("Exemplo: <em>(31)8851-9898</em>."),
    )
    telefones = GenericRelation("contatos.Telefone")
    foto = models.ImageField(
        _("foto"),
        upload_to="imagens/casas",
        width_field="foto_largura",
        height_field="foto_altura",
        blank=True,
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    data_instalacao = models.DateField(
        _("data de instalação da Casa Legislativa"), null=True, blank=True
    )
    brasao = models.ImageField(
        _("brasão"),
        upload_to="imagens/casas/brasao",
        width_field="brasao_largura",
        height_field="brasao_altura",
        blank=True,
        help_text=_(
            "Trate a imagem para que ela fique com cerca de 120x120 pixels"
        ),
    )
    brasao_largura = models.SmallIntegerField(editable=False, null=True)
    brasao_altura = models.SmallIntegerField(editable=False, null=True)

    @classmethod
    def _mathnames(cls, nome, orgaos):
        for o, nome_canonico in orgaos:
            ratio = SequenceMatcher(
                None, to_ascii(nome).lower(), nome_canonico
            ).ratio()
            if ratio > 0.9:
                yield (o, ratio)

    @classmethod
    def get_semelhantes(cls, nome, orgaos=None):
        if orgaos is None:
            orgaos = [
                (o, f"{to_ascii(o.nome)} - {o.uf_sigla}".lower())
                for o in Orgao.objects.all()
                .order_by()
                .annotate(uf_sigla=models.F("municipio__uf__sigla"))
            ]
        return sorted(
            cls._mathnames(nome, orgaos),
            key=lambda m: m[1],
        )

    class Meta:
        ordering = ("nome",)
        verbose_name = _("órgão")
        verbose_name_plural = _("órgãos")

    def lista_gerentes(self):
        return [g.get_apelido() for g in self.gerentes_interlegis.all()]

    @property
    def num_parlamentares(self):
        return self.parlamentar_set.count()

    @property
    def telefone(self):
        if self.telefone_geral:
            return self.telefone_geral
        telefone = self.telefones.first()
        if telefone:
            return telefone.numero
        return ""

    @property
    def presidente(self):
        return self.parlamentar_set.filter(presidente=True).first()

    @property
    def contato_interlegis(self):
        return self.funcionario_set.filter(setor="contato_interlegis").first()

    def get_sigla(self):
        return self.sigla or "".join(
            [
                w[0]
                for w in self.nome.split()
                if w.lower() not in ["da", "de", "do"]
            ]
        )

    def __str__(self):
        return _(f"{self.nome} ({self.municipio.uf.sigla})")

    def clean(self):
        if (
            hasattr(self, "tipo")
            and hasattr(self, "municipio")
            and self.tipo.legislativo
        ):
            if (
                Orgao.objects.filter(tipo=self.tipo, municipio=self.municipio)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError(
                    _("Já existe um(a) %(tipo)s em %(municipio)s"),
                    code="integrity",
                    params={"tipo": self.tipo, "municipio": self.municipio},
                )

    def save(self, *args, **kwargs):
        address_changed = False

        if self.pk is not None:
            original = Orgao.objects.get(pk=self.pk)
            if (
                self.logradouro != original.logradouro
                or self.bairro != original.bairro
                or self.municipio != original.municipio
                or self.cep != original.cep
            ):
                address_changed = True
        else:
            address_changed = True

        if address_changed:
            self.ult_alt_endereco = timezone.localtime()

        # Mascara corretamente o CNPJ
        if (
            self.cnpj != ""
            and valida_cnpj(self.cnpj)
            and self.cnpj != mask_cnpj(self.cnpj)
        ):
            self.cnpj = mask_cnpj(self.cnpj)

        return super(Orgao, self).save(*args, **kwargs)


class Funcionario(models.Model):
    SETOR_CHOICES = [
        ("presidente", _("Presidente")),
        ("contato_interlegis", _("Contato Interlegis")),
        ("infraestrutura_fisica", _("Infraestrutura Física")),
        ("estrutura_de_ti", _("Estrutura de TI")),
        (
            "organizacao_do_processo_legislativo",
            _("Organização do Processo Legislativo"),
        ),
        ("producao_legislativa", _("Produção Legislativa")),
        (
            "estrutura_de_comunicacao_social",
            _("Estrutura de Comunicação Social"),
        ),
        ("estrutura_de_recursos_humanos", _("Estrutura de Recursos Humanos")),
        ("gestao", _("Gestão")),
        ("outros", _("Outros")),
    ]
    SEXO_CHOICES = [("M", _("Masculino")), ("F", _("Feminino"))]

    casa_legislativa = models.ForeignKey(
        Orgao,
        on_delete=models.CASCADE,
        verbose_name=_("órgão"),
    )
    nome = models.CharField(_("nome completo"), max_length=60, blank=False)
    sexo = models.CharField(
        _("sexo"), max_length=1, choices=SEXO_CHOICES, default="M"
    )
    data_nascimento = models.DateField(
        _("data de nascimento"), blank=True, null=True
    )
    cpf = models.CharField(_("CPF"), max_length=20, blank=True)
    identidade = models.CharField(
        _("Identidade (RG)"),
        max_length=30,
        blank=True,
        help_text=_("Informe o RG e o órgão emissor."),
    )
    nota = models.CharField(
        _("telefones"), max_length=250, null=True, blank=True
    )
    email = models.CharField(_("e-mail"), max_length=250, blank=True)
    endereco = models.CharField(_("endereço"), max_length=100, blank=True)
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        verbose_name=_("municipio"),
        null=True,
        blank=True,
    )
    bairro = models.CharField(_("bairro"), max_length=100, blank=True)
    cep = models.CharField(_("CEP"), max_length=10, blank=True)
    redes_sociais = models.TextField(
        _("redes sociais"), help_text=_("Colocar um por linha"), blank=True
    )
    cargo = models.CharField(_("cargo"), max_length=100, null=True, blank=True)
    funcao = models.CharField(
        _("função"), max_length=100, null=True, blank=True
    )
    setor = models.CharField(
        _("setor"), max_length=100, choices=SETOR_CHOICES, default="outros"
    )
    tempo_de_servico = models.CharField(
        _("tempo de serviço"), max_length=50, null=True, blank=True
    )
    ult_alteracao = models.DateTimeField(
        _("última alteração"),
        null=True,
        blank=True,
        editable=True,
        auto_now=True,
    )
    desativado = models.BooleanField(_("desativado"), default=False)
    observacoes = models.TextField(_("observações"), blank=True)

    class Meta:
        ordering = ("nome",)
        verbose_name = _("contato da Casa Legislativa")
        verbose_name_plural = _("contatos da Casa Legislativa")

    def __str__(self):
        return self.nome
