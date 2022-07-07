from collections import OrderedDict
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder

from sigi.apps.convenios.models import Projeto


class Categoria(models.Model):
    TIPO_CHOICES = (
        ("C", _("Solicitação de convênio (ACT)")),
        ("O", _("Outras")),
    )
    nome = models.CharField(_("Categoria"), max_length=50)
    descricao = models.TextField(_("descrição"), blank=True, null=True)
    tipo = models.CharField(
        _("Tipo de solicitação"),
        max_length=1,
        choices=TIPO_CHOICES,
        default="O",
    )
    projeto = models.ForeignKey(
        Projeto,
        verbose_name=_("projeto"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        limit_choices_to=(
            ~models.Q(texto_oficio="") & ~models.Q(modelo_minuta="")
        ),
    )

    class Meta:
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")
        ordering = ("nome",)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.tipo == "C":
            Categoria.objects.filter(tipo="C").update(tipo="O")
        return super().save(*args, **kwargs)


class TipoContato(models.Model):
    descricao = models.CharField(_("Descrição"), max_length=50)
    ind_site = models.BooleanField(_("Contato pelo SIGI"), default=False)

    class Meta:
        verbose_name = _("Tipo de contato")
        verbose_name_plural = _("Tipos de contato")

    def __str__(self):
        return self.descricao

    def save(self, *args, **kwargs):
        if self.ind_site:
            TipoContato.objects.filter(ind_site=True).update(ind_site=False)
        return super().save(*args, **kwargs)


class Ocorrencia(models.Model):
    STATUS_ABERTO = 1
    STATUS_REABERTO = 2
    STATUS_RESOLVIDO = 3
    STATUS_FECHADO = 4
    STATUS_DUPLICADO = 5

    STATUS_CHOICES = (
        (STATUS_ABERTO, _("Aberto")),
        (STATUS_REABERTO, _("Reaberto")),
        (STATUS_RESOLVIDO, _("Resolvido")),
        (STATUS_FECHADO, _("Fechado")),
        (STATUS_DUPLICADO, _("Duplicado")),
    )

    PRIORITY_CHOICES = (
        (1, _("Altíssimo")),
        (2, _("Alto")),
        (3, _("Normal")),
        (4, _("Baixo")),
        (5, _("Baixíssimo")),
    )

    INFO_KEYS = (
        ("casa_legislativa", _("Casa legislativa")),
        ("presidente", _("Presidente")),
        ("contato", _("Contato Interlegis")),
        ("documento", _("Documento assinado")),
    )

    casa_legislativa = models.ForeignKey(
        "casas.Orgao",
        on_delete=models.CASCADE,
        verbose_name=_("Casa Legislativa"),
    )
    data_criacao = models.DateField(
        _("Data de criação"), null=True, blank=True, auto_now_add=True
    )
    data_modificacao = models.DateField(
        _("Data de modificação"), null=True, blank=True, auto_now=True
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, verbose_name=_("Categoria")
    )
    tipo_contato = models.ForeignKey(
        TipoContato, on_delete=models.PROTECT, verbose_name=_("Tipo de contato")
    )
    assunto = models.CharField(_("Assunto"), max_length=200)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=1)
    prioridade = models.IntegerField(
        _("Prioridade"), choices=PRIORITY_CHOICES, default=3
    )
    descricao = models.TextField(
        _("descrição"),
        blank=True,
    )
    resolucao = models.TextField(
        _("resolução"),
        blank=True,
    )
    servidor_registro = models.ForeignKey(
        "servidores.Servidor",
        on_delete=models.PROTECT,
        verbose_name=_("Servidor que registrou a ocorrência"),
    )
    ticket = models.PositiveIntegerField(
        _("Número do ticket"),
        blank=True,
        null=True,
        help_text=_("Número do ticket no osTicket"),
    )
    processo_sigad = models.CharField(
        _("Nº processo SIGAD"), max_length=20, blank=True
    )
    infos = models.JSONField(
        _("dados estruturados"),
        blank=True,
        null=True,
        encoder=DjangoJSONEncoder,
        editable=False,
    )
    casa_foto = models.ImageField(
        _("foto da Casa"),
        upload_to="ocorrencias/img/",
        blank=True,
        null=True,
        editable=False,
    )
    casa_brasao = models.ImageField(
        _("brasão da casa"),
        upload_to="ocorrencias/img/",
        blank=True,
        null=True,
        editable=True,
    )

    class Meta:
        verbose_name = _("ocorrência")
        verbose_name_plural = _("ocorrências")
        ordering = [
            "prioridade",
            "data_modificacao",
            "data_criacao",
        ]

    def __str__(self):
        return _(f"{self.casa_legislativa}: {self.assunto}")

    def clean(self):
        if (
            self.ticket is not None
            and Ocorrencia.objects.exclude(pk=self.pk)
            .filter(ticket=self.ticket)
            .exists()
        ):
            raise ValidationError(
                {
                    "ticket": _(
                        "Já existe ocorrência registrada para este ticket"
                    )
                }
            )
        return super(Ocorrencia, self).clean()

    def get_ticket_url(self):
        return mark_safe(settings.OSTICKET_URL % self.ticket)

    def get_infos_details(self):
        infos = self.infos or {}
        return OrderedDict(
            {key: [key in infos, label] for key, label in Ocorrencia.INFO_KEYS}
        )


class Comentario(models.Model):
    ocorrencia = models.ForeignKey(
        Ocorrencia,
        on_delete=models.CASCADE,
        verbose_name=_("Ocorrência"),
        related_name="comentarios",
    )
    data_criacao = models.DateTimeField(
        _("Data de criação"), null=True, blank=True, auto_now_add=True
    )
    descricao = models.TextField(_("Descrição"), blank=True, null=True)
    usuario = models.ForeignKey(
        "servidores.Servidor",
        on_delete=models.PROTECT,
        verbose_name=_("Usuário"),
    )
    novo_status = models.IntegerField(
        _("Novo status"),
        choices=Ocorrencia.STATUS_CHOICES,
        blank=True,
        null=True,
    )
    interno = models.BooleanField(_("Comentário interno"), default=False)

    class Meta:
        verbose_name = _("comentário")
        verbose_name_plural = _("comentários")
        ordering = ["-data_criacao"]

    def save(self, *args, **kwargs):
        if self.novo_status and (self.novo_status != self.ocorrencia.status):
            self.ocorrencia.status = self.novo_status
            self.ocorrencia.save()
        super(Comentario, self).save(*args, **kwargs)


class Anexo(models.Model):
    ocorrencia = models.ForeignKey(
        Ocorrencia, on_delete=models.CASCADE, verbose_name=_("ocorrência")
    )
    arquivo = models.FileField(
        _("Arquivo anexado"),
        upload_to="apps/ocorrencia/anexo/arquivo",
        max_length=500,
    )
    descricao = models.CharField(_("descrição do anexo"), max_length=70)
    data_pub = models.DateTimeField(
        _("data da publicação do anexo"),
        null=True,
        blank=True,
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-data_pub",)
        verbose_name = _("Anexo")
        verbose_name_plural = _("Anexos")

    def __str__(self):
        return _(f"{self.arquivo.name}: {self.descricao}")
