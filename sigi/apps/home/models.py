from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _


class Cards(models.Model):
    TIPO_CHOICES = (
        ("T", _("Tabela de dados")),
        ("C", _("Gráfico")),
    )
    codigo = models.CharField(_("código"), max_length=20)
    tipo = models.CharField(_("tipo"), max_length=1, choices=TIPO_CHOICES)
    nome_url = models.CharField(_("nome da URL de dados"), max_length=30)
    query_string = models.CharField(
        _("query string"),
        max_length=100,
        blank=True,
    )
    link_acao = models.BooleanField(_("possui link de ação"), default=False)
    titulo = models.CharField(_("título"), max_length=100)
    descricao = models.TextField(_("descrição"))
    categoria = models.CharField(
        _("categoria"), max_length=40, default=_("Geral")
    )
    ordem = models.PositiveSmallIntegerField(
        _("posição na categoria"), default=0
    )
    default = models.BooleanField(
        _("card padrão"),
        default=False,
        help_text=_(
            "Indica se este card deve ser mostrado para usuários anônimos ou "
            "que não personalizaram seu dashboard"
        ),
    )

    class Meta:
        ordering = ("categoria", "ordem", "titulo")
        verbose_name = _("card")
        verbose_name_plural = _("cards")

    def __str__(self):
        return _(f"{self.titulo} ({self.categoria})")


class Dashboard(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)
    categoria = models.CharField(
        _("categoria personalizada"),
        max_length=40,
        blank=True,
        help_text=_(
            "Deixando em branco será utilizada a categoria padrão do card"
        ),
    )
    ordem = models.PositiveSmallIntegerField(
        _("posição na categoria"), default=0
    )

    class Meta:
        ordering = ("usuario", "categoria", "ordem")
        verbose_name = _("dashboard")
        verbose_name_plural = _("dashboards")

    def __str__(self):
        return _(f"{self.usuario.get_full_name()} - {self.card}")
