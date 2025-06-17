import re
from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
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
    capacidade = models.PositiveBigIntegerField(
        _("capacidade"),
        default=0,
        help_text=_("Número de acentos ou lotação máxima do espaço"),
    )
    reserva_eventos = models.BooleanField(
        _("reserva para eventos"),
        default=False,
        help_text=_("Pode ser reservado para eventos cadastrados no SIGI"),
    )
    id_sala = models.PositiveIntegerField(
        _("ID da sala"),
        blank=True,
        null=True,
        help_text=_("ID da sala no sistema de reserva de salas do ILB"),
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
    id_equipamento = models.PositiveBigIntegerField(
        _("ID do equipamento"),
        blank=True,
        null=True,
        unique=True,
        help_text=_("ID do equipamento no sistema de reserva de salas do ILB"),
    )

    class Meta:
        verbose_name = _("recurso")
        verbose_name_plural = _("recursos")
        ordering = ("nome",)

    def __str__(self):
        return _(f"{self.sigla} - {self.nome}")


class Reserva(models.Model):
    STATUS_ATIVO = "A"
    STATUS_CANCELADO = "C"
    STATUS_CONFLITO = "O"

    STATUS_CHOICES = (
        (STATUS_ATIVO, _("Ativo")),
        (STATUS_CANCELADO, _("Cancelado")),
        (STATUS_CONFLITO, _("Conflito de datas")),
    )

    status = models.CharField(
        _("status"),
        max_length=1,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVO,
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
    data_inicio = models.DateField(_("data início"))
    data_termino = models.DateField(_("data término"))
    hora_inicio = models.TimeField(_("hora início"))
    hora_termino = models.TimeField(_("hora término"))
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
    id_reserva = models.PositiveBigIntegerField(
        _("ID da reserva"), blank=True, null=True, editable=False, unique=True
    )
    data_ult_atualizacao = models.DateTimeField(
        _("data da última atualização"), blank=True, null=True, editable=False
    )

    class Meta:
        verbose_name = _("reserva")
        verbose_name_plural = _("reservas")
        ordering = ("data_inicio", "hora_inicio", "espaco", "proposito")

    def __str__(self):
        return _(f"{self.proposito} em {self.espaco.nome}")

    def clean(self):
        if (
            self.data_inicio is None
            or self.data_termino is None
            or self.hora_inicio is None
            or self.hora_termino is None
        ):
            # Não tem como fazer as verificações de data.
            # Deixa seguir para que o clean_fields lance as exceções
            return super().clean()

        if self.data_inicio > self.data_termino:
            raise ValidationError(
                _("Data de início deve ser anterior à data de término")
            )
        if self.hora_inicio and self.hora_termino:
            if (
                self.data_inicio == self.data_termino
                and self.hora_inicio > self.hora_termino
            ):
                raise ValidationError(
                    _("Hora de início deve ser anterior à hora de término")
                )

        if not hasattr(self, "espaco"):
            # Se não informou o espaço, não há como verificar conflito
            # Deixa seguir para o clean_fields lançar a exceção
            return super().clean()

        reservas_conflitantes = self.get_conflitantes()
        if reservas_conflitantes.exists():
            if self.status == Reserva.STATUS_CONFLITO:
                # Marco as conflitantes com status CONFLITO e deixo seguir
                reservas_conflitantes.update(status=Reserva.STATUS_CONFLITO)
            elif self.status == Reserva.STATUS_ATIVO:
                # Não pode salvar assim. Lança exceção
                erro_txt = render_to_string(
                    "espacos/snippets/alerta_conflitos_snippet.html",
                    context={"reservas_conflitantes": reservas_conflitantes},
                )
                raise ValidationError(mark_safe(erro_txt))
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def get_conflitantes(self):
        return (
            Reserva.objects.exclude(id=self.pk)
            .exclude(status=Reserva.STATUS_CANCELADO)
            .filter(
                espaco=self.espaco,
                data_inicio__lte=self.data_termino,
                data_termino__gte=self.data_inicio,
                hora_inicio__lte=self.hora_termino,
                hora_termino__gte=self.hora_inicio,
            )
        )

    def get_sigad_url(self):
        m = re.match(
            r"(?P<orgao>00100|00200)\.(?P<sequencial>\d{6})/(?P<ano>"
            r"\d{4})-\d{2}",
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
