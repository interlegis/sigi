import re
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _


class Espaco(models.Model):
    nome = models.CharField(_("nome"), max_length=100)
    sigla = models.CharField(_("sigla"), max_length=20)
    descricao = models.TextField(_("descrição"), blank=True)
    local = models.CharField(
        _("local"),
        max_length=100,
        help_text=_(
            "Indique o prédio/bloco/sala onde este espaço está localizado."
        ),
    )

    class Meta:
        verbose_name = _("espaço")
        verbose_name_plural = _("espaços")
        ordering = ("nome",)

    def __str__(self):
        return _(f"{self.sigla} - {self.nome}")


class Recurso(models.Model):
    nome = models.CharField(_("nome"), max_length=100)
    sigla = models.CharField(_("sigla"), max_length=20)
    descricao = models.TextField(_("descrição"), blank=True)

    class Meta:
        verbose_name = _("recurso")
        verbose_name_plural = _("recursos")
        ordering = ("nome",)

    def __str__(self):
        return _(f"{self.sigla} - {self.nome}")


class Reserva(models.Model):
    STATUS_ATIVO = "A"
    STATUS_CANCELADO = "C"

    STATUS_CHOICES = (
        (STATUS_ATIVO, _("Ativo")),
        (STATUS_CANCELADO, _("Cancelado")),
    )

    status = models.CharField(
        _("status"),
        max_length=1,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVO,
        editable=False,
    )
    espaco = models.ForeignKey(
        Espaco, verbose_name=_("espaço"), on_delete=models.PROTECT
    )
    proposito = models.CharField(
        _("propósito"),
        max_length=100,
        help_text=_(
            "Indique o propósito da reserva (nome do evento, indicativo da "
            "reunião, aula, apresentação, etc.)"
        ),
    )
    virtual = models.BooleanField(_("virtual"), default=False)
    total_participantes = models.PositiveIntegerField(
        _("total de participantes"), default=0
    )
    data_pedido = models.DateField(_("data do pedido"), blank=True, null=True)
    inicio = models.DateTimeField(_("data/hora de início"))
    termino = models.DateTimeField(_("data/hora de término"))
    num_processo = models.CharField(
        _("número do processo SIGAD"),
        max_length=20,
        blank=True,
        help_text=_("Formato:<em>XXXXX.XXXXXX/XXXX-XX</em>"),
    )
    informacoes = models.TextField(
        _("informações adicionais"),
        blank=True,
        help_text=_(
            "Utilize para anotar informações adicionais e demais detalhes "
            "sobre a reserva"
        ),
    )
    solicitante = models.CharField(
        _("senador/autoridade solicitante"),
        max_length=100,
        help_text=_(
            "indique o nome do Senador, autoridade, pessoa ou setor "
            "solicitante da reserva"
        ),
    )
    contato = models.CharField(
        _("pessoa de contato"),
        max_length=100,
        blank=True,
        help_text=_(
            "Indique o nome da(s) pessoa(s) de contato para tratar "
            "assuntos da reserva."
        ),
    )
    telefone_contato = models.CharField(
        _("telefone de contato"),
        max_length=100,
        blank=True,
        help_text=_(
            "Indique o telefone/ramal da pessoa responsável pela reserva."
        ),
    )

    class Meta:
        verbose_name = _("reserva")
        verbose_name_plural = _("reservas")
        ordering = ("inicio", "espaco", "proposito")

    def __str__(self):
        return _(f"{self.proposito} em {self.espaco.nome}")

    def clean(self):
        if self.inicio > self.termino:
            raise ValidationError(
                _("Data de início deve ser anterior à data de término")
            )
        if (
            Reserva.objects.exclude(id=self.pk)
            .filter(
                espaco=self.espaco,
                inicio__lte=self.termino,
                termino__gte=self.inicio,
            )
            .exists()
        ):
            raise ValidationError(
                _(
                    "Já existe um evento neste mesmo espaço que conflita com "
                    "as datas solicitadas"
                )
            )
        return super().clean()

    def get_sigad_url(self):
        m = re.match(
            "(?P<orgao>00100|00200)\.(?P<sequencial>\d{6})/(?P<ano>"
            "\d{4})-\d{2}",
            self.num_processo,
        )
        if m:
            return (
                '<a href="https://intra.senado.leg.br/'
                "sigad/novo/protocolo/impressao.asp?area=processo"
                "&txt_numero_orgao={orgao}"
                "&txt_numero_sequencial={sequencial}"
                '&txt_numero_ano={ano}"'
                ' target="_blank">{processo}</a>'
            ).format(processo=self.num_processo, **m.groupdict())
        return self.num_processo


class RecursoSolicitado(models.Model):
    reserva = models.ForeignKey(
        Reserva, verbose_name=_("reserva"), on_delete=models.CASCADE
    )
    recurso = models.ForeignKey(
        Recurso, verbose_name=_("recurso"), on_delete=models.PROTECT
    )
    quantidade = models.FloatField(_("quantidade"), default=0.0)
    observacoes = models.TextField(_("observações"), blank=True)

    class Meta:
        verbose_name = _("recurso solicitado")
        verbose_name_plural = _("recursos solicitados")
        ordering = ("recurso",)

    def __str__(self):
        return _(f"{self.recurso} para {self.reserva}")
