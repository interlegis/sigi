from django.db import models
from django.utils.translation import gettext as _
from sigi.apps.casas.models import Orgao


class Partido(models.Model):
    nome = models.CharField(_("nome"), max_length=50)
    sigla = models.CharField(_("sigla"), max_length=20)
    legenda = models.PositiveIntegerField(_("nº da legenda"), default=0)

    class Meta:
        ordering = ("nome",)

    def __str__(self):
        return _(f"{self.sigla} - {self.nome}")


class Parlamentar(models.Model):
    STATUS_CHOICE = (
        ("E", _("Em exercício")),
        ("S", _("Suplente")),
        ("I", _("Inativo")),
    )
    casa_legislativa = models.ForeignKey(
        Orgao, verbose_name=_("casa legislativa"), on_delete=models.CASCADE
    )
    partido = models.ForeignKey(
        Partido, verbose_name=_("partido"), on_delete=models.CASCADE
    )
    ano_eleicao = models.PositiveIntegerField(
        _("Ano de eleição"), blank=True, null=True
    )
    status_mandato = models.CharField(
        _("status do mandato"), max_length=1, choices=STATUS_CHOICE, default="E"
    )
    presidente = models.BooleanField(_("presidente"), default=False)
    nome_completo = models.CharField(max_length=128)
    nome_parlamentar = models.CharField(max_length=35, blank=True)
    foto = models.ImageField(
        max_length=200,
        upload_to="parlamentares/parlamentar/fotos",
        width_field="foto_largura",
        height_field="foto_altura",
        blank=True,
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    data_nascimento = models.DateField(
        _("data de nascimento"),
        blank=True,
        null=True,
    )
    cpf = models.CharField(_("CPF"), max_length=20, blank=True)
    identidade = models.CharField(
        _("Identidade (RG)"),
        max_length=30,
        blank=True,
        help_text=_("Informe o RG e o órgão emissor."),
    )
    telefones = models.CharField(
        _("telefones"), max_length=250, null=True, blank=True
    )
    email = models.EmailField(_("e-mail"), blank=True)
    redes_sociais = models.TextField(
        _("redes sociais"), help_text=_("Colocar um por linha"), blank=True
    )
    ult_alteracao = models.DateTimeField(
        _("última alteração"),
        null=True,
        blank=True,
        editable=True,
        auto_now=True,
    )
    observacoes = models.TextField(_("observações"), blank=True)
    sequencial_tse = models.CharField(
        _("Sequencial TSE"),
        max_length=20,
        blank=True,
        default="",
        editable=False,
    )
    flag_importa = models.CharField(
        max_length=1, blank=True, default="", editable=False
    )

    class Meta:
        ordering = (
            "status_mandato",
            "presidente",
            "nome_completo",
        )
        verbose_name_plural = _("parlamentares")

    def __str__(self):
        return self.nome_completo

    def save(self, *args, **kwargs):
        if self.presidente:
            self.casa_legislativa.parlamentar_set.filter(
                presidente=True
            ).update(presidente=False)
        return super().save(*args, **kwargs)
