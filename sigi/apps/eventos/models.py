import re
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from sigi.apps.casas.models import Orgao
from sigi.apps.contatos.models import Municipio
from sigi.apps.servidores.models import Servidor
from django.core.exceptions import ValidationError
from tinymce.models import HTMLField


class TipoEvento(models.Model):
    CATEGORIA_CHOICES = (
        ("C", _("Curso")),
        ("E", _("Encontro")),
        ("O", _("Oficina")),
        ("S", _("Seminário")),
        ("V", _("Visita")),
    )
    nome = models.CharField(_("Nome"), max_length=100)
    categoria = models.CharField(
        _("Categoaria"), max_length=1, choices=CATEGORIA_CHOICES
    )

    class Meta:
        ordering = ("nome",)
        verbose_name, verbose_name_plural = _("Tipo de evento"), _(
            "Tipos de evento"
        )

    def __str__(self):
        return self.nome


class Evento(models.Model):
    STATUS_CHOICES = (
        ("E", _("Em planejamento")),
        ("G", _("Aguardando abertura SIGAD")),
        ("P", _("Previsão")),
        ("A", _("A confirmar")),
        ("O", _("Confirmado")),
        ("R", _("Realizado")),
        ("C", _("Cancelado")),
        ("Q", _("Arquivado")),
    )

    tipo_evento = models.ForeignKey(
        TipoEvento,
        on_delete=models.PROTECT,
    )
    nome = models.CharField(_("Nome do evento"), max_length=100)
    descricao = models.TextField(_("Descrição do evento"))
    virtual = models.BooleanField(_("Virtual"), default=False)
    solicitante = models.CharField(_("Solicitante"), max_length=100)
    num_processo = models.CharField(
        _("número do processo SIGAD"),
        max_length=20,
        blank=True,
        help_text=_("Formato:<em>XXXXX.XXXXXX/XXXX-XX</em>"),
    )
    data_pedido = models.DateField(
        _("Data do pedido"),
        null=True,
        blank=True,
        help_text=_("Data em que o pedido do Gabinete chegou à COPERI"),
    )
    data_inicio = models.DateTimeField(
        _("Data/hora do Início"), null=True, blank=True
    )
    data_termino = models.DateTimeField(
        _("Data/hora do Termino"), null=True, blank=True
    )
    carga_horaria = models.PositiveIntegerField(_("carga horária"), default=0)
    casa_anfitria = models.ForeignKey(
        Orgao,
        on_delete=models.PROTECT,
        verbose_name=_("Casa anfitriã"),
        blank=True,
        null=True,
    )
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT)
    local = models.TextField(_("Local do evento"), blank=True)
    observacao = models.TextField(_("Observações e anotações"), blank=True)
    publico_alvo = models.TextField(_("Público alvo"), blank=True)
    total_participantes = models.PositiveIntegerField(
        _("Total de participantes"),
        default=0,
        help_text=_(
            "Se informar quantidade de participantes na aba de "
            "convites, este campo será ajustado com a somatória "
            "dos participantes naquela aba."
        ),
    )
    status = models.CharField(_("Status"), max_length=1, choices=STATUS_CHOICES)
    data_cancelamento = models.DateField(
        _("Data de cancelamento"), blank=True, null=True
    )
    motivo_cancelamento = models.TextField(
        _("Motivo do cancelamento"), blank=True
    )

    class Meta:
        ordering = ("-data_inicio",)
        verbose_name, verbose_name_plural = _("Evento"), _("Eventos")

    def __str__(self):
        return _(
            f"{self.nome} ({self.tipo_evento}): "
            f"de {self.data_inicio} a {self.data_termino}"
        )

    def get_absolute_url(self):
        return reverse("eventos-evento", args=[self.id])

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

    def save(self, *args, **kwargs):
        if self.status != "C":
            self.data_cancelamento = None
            self.motivo_cancelamento = ""
        if self.data_inicio > self.data_termino:
            raise ValidationError(
                _("Data de término deve ser posterior à " "data de início")
            )
        total = self.convite_set.aggregate(total=Sum("qtde_participantes"))
        total = total["total"]
        if total and total > 0:
            self.total_participantes = total
        return super(Evento, self).save(*args, **kwargs)


class Funcao(models.Model):
    nome = models.CharField(_("Função na equipe de evento"), max_length=100)
    descricao = models.TextField(_("Descrição da função"))

    class Meta:
        ordering = ("nome",)
        verbose_name, verbose_name_plural = _("Função"), _("Funções")

    def __str__(self):
        return self.nome


class Equipe(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    membro = models.ForeignKey(
        Servidor, on_delete=models.PROTECT, related_name="equipe_evento"
    )
    funcao = models.ForeignKey(
        Funcao, on_delete=models.PROTECT, verbose_name=_("Função na equipe")
    )
    assina_oficio = models.BooleanField(
        _("Assina ofício de comparecimento"), default=False
    )
    observacoes = models.TextField(_("Observações"), blank=True)

    class Meta:
        ordering = (
            "evento",
            "funcao",
            "membro",
        )
        verbose_name, verbose_name_plural = _("Membro da equipe"), _(
            "Membros da equipe"
        )

    def __str__(self):
        return _(f"{self.membro} ({self.funcao})")


class Convite(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    casa = models.ForeignKey(
        Orgao, on_delete=models.PROTECT, verbose_name=_("Casa convidada")
    )
    servidor = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        verbose_name=_("Servidor que convidou"),
    )
    data_convite = models.DateField(_("Data do convite"))
    aceite = models.BooleanField(_("Aceitou o convite"), default=False)
    participou = models.BooleanField(_("Participou do evento"), default=False)
    qtde_participantes = models.PositiveIntegerField(
        _("número de participantes"), default=0
    )
    nomes_participantes = models.TextField(
        _("nome dos participantes"),
        blank=True,
        help_text=_("Favor colocar um participante por linha"),
    )

    class Meta:
        ordering = ("evento", "casa", "-data_convite")
        unique_together = ("evento", "casa")
        verbose_name = _("Casa convidada")
        verbose_name_plural = _("Casas convidadas")


class Modulo(models.Model):
    TIPO_CHOICES = (
        ("A", _("Aula")),
        ("P", _("Palestra")),
        ("R", _("Apresentação")),
    )
    evento = models.ForeignKey(
        Evento, verbose_name=_("Evento"), on_delete=models.CASCADE
    )
    nome = models.CharField(_("Nome"), max_length=100)
    descricao = models.TextField(_("Descrição do módulo"))
    tipo = models.CharField(_("Tipo"), max_length=1, choices=TIPO_CHOICES)
    inicio = models.DateTimeField(
        _("Data/hora de início"), null=True, blank=True
    )
    termino = models.DateTimeField(
        _("Data/hora de término"), null=True, blank=True
    )
    carga_horaria = models.PositiveIntegerField(_("carga horária"), default=0)
    apresentador = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        related_name="modulo_apresentador",
        null=True,
        blank=True,
        verbose_name=_("Apresentador"),
    )
    monitor = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        related_name="modulo_monitor",
        null=True,
        blank=True,
        verbose_name=_("Monitor"),
        help_text=_("Monitor, mediador, auxiliar, etc."),
    )
    qtde_participantes = models.PositiveIntegerField(
        _("número de participantes"),
        default=0,
        help_text=_(
            "Deixar Zero significa que todos os participantes "
            "do evento participaram do módulo"
        ),
    )

    class Meta:
        ordering = ("inicio",)
        verbose_name = _("Módulo do evento")
        verbose_name_plural = _("Módulos do evento")

    def __str__(self):
        return _(f"{self.nome} ({self.get_tipo_display()})")


class ModeloDeclaracao(models.Model):
    FORMATO_CHOICES = (
        ("A4 portrait", _("A4 retrato")),
        ("A4 landscape", _("A4 paisagem")),
        ("letter portrait", _("Carta retrato")),
        ("letter landscape", _("Carta paisagem")),
    )
    nome = models.CharField(_("Nome do modelo"), max_length=100)
    formato = models.CharField(
        _("Formato da página"),
        max_length=30,
        choices=FORMATO_CHOICES,
        default=FORMATO_CHOICES[0][0],
    )
    margem = models.PositiveIntegerField(
        _("Margem"), help_text=_("Margem da página em centímetros"), default=4
    )
    texto = HTMLField(
        _("Texto da declaração"),
        help_text=_(
            "Use as seguintes marcações:<ul><li>{{ casa.nome }} para o"
            " nome da Casa Legislativa / órgão</li>"
            "<li>{{ casa.municipio.uf.sigla }} para a sigla da UF da "
            "Casa legislativa</li><li>{{ nome }} "
            "para o nome do visitante</li><li>{{ data }} para a data "
            "de emissão da declaração</li><li>{{ evento.data_inicio }}"
            " para a data/hora do início da visita</li>"
            "<li>{{ evento.data_termino }} para a data/hora do "
            "término da visita</li><li>{{ evento.nome }} para o nome "
            "do evento</li><li>{{ evento.descricao }} para a descrição"
            " do evento</li></ul>"
        ),
    )

    class Meta:
        verbose_name = _("modelo de declaração")
        verbose_name_plural = _("modelos de declaração")

    def __str__(self):
        return _(f"{self.nome} ({self.get_formato_display()})")


class Anexo(models.Model):
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, verbose_name=_("evento")
    )
    # caminho no sistema para o documento anexo
    arquivo = models.FileField(
        upload_to="apps/eventos/anexo/arquivo", max_length=500
    )
    descricao = models.CharField(_("descrição"), max_length=70)
    data_pub = models.DateTimeField(
        _("data da publicação do anexo"), default=timezone.localtime
    )
    convite = models.ForeignKey(
        Convite, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ("-data_pub",)

    def __str__(self):
        return _(f"{self.descricao} publicado em {self.data_pub}")
