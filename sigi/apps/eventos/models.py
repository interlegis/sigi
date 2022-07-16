import datetime
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
    CATEGORIA_CURSO = "C"
    CATEGORIA_ENCONTRO = "E"
    CATEGORIA_OFICINA = "O"
    CATEGORIA_SEMINARIO = "S"
    CATEGORIA_VISITA = "V"

    CATEGORIA_CHOICES = (
        (CATEGORIA_CURSO, _("Curso")),
        (CATEGORIA_ENCONTRO, _("Encontro")),
        (CATEGORIA_OFICINA, _("Oficina")),
        (CATEGORIA_SEMINARIO, _("Seminário")),
        (CATEGORIA_VISITA, _("Visita")),
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
    STATUS_PLANEJAMENTO = "E"
    STATUS_AGUARDANDOSIGAD = "G"
    STATUS_PREVISAO = "P"
    STATUS_ACONFIRMAR = "A"
    STATUS_CONFIRMADO = "O"
    STATUS_REALIZADO = "R"
    STATUS_CANCELADO = "C"
    STATUS_ARQUIVADO = "Q"

    STATUS_CHOICES = (
        (STATUS_PLANEJAMENTO, _("Em planejamento")),
        (STATUS_AGUARDANDOSIGAD, _("Aguardando abertura SIGAD")),
        (STATUS_PREVISAO, _("Previsão")),
        (STATUS_ACONFIRMAR, _("A confirmar")),
        (STATUS_CONFIRMADO, _("Confirmado")),
        (STATUS_REALIZADO, _("Realizado")),
        (STATUS_CANCELADO, _("Cancelado")),
        (STATUS_ARQUIVADO, _("Arquivado")),
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
        if self.status != Evento.STATUS_CANCELADO:
            self.data_cancelamento = None
            self.motivo_cancelamento = ""
        if self.data_inicio > self.data_termino:
            raise ValidationError(
                _("Data de término deve ser posterior à data de início")
            )
        total = self.convite_set.aggregate(total=Sum("qtde_participantes"))
        total = total["total"]
        if total and total > 0:
            self.total_participantes = total
        if self.status in [
            Evento.STATUS_PLANEJAMENTO,
            Evento.STATUS_AGUARDANDOSIGAD,
            Evento.STATUS_PREVISAO,
            Evento.STATUS_ACONFIRMAR,
        ]:
            if (
                self.cronograma_set.count() == 0
                and self.tipo_evento.checklist_set.count() > 0
            ):
                cronograma_list = []
                for item in self.tipo_evento.checklist_set.all():
                    cronograma_list.append(
                        Cronograma(
                            evento=self,
                            etapa=item.etapa,
                            nome=item.nome,
                            descricao=item.descricao,
                            duracao=item.duracao,
                            dependencia=item.dependencia,
                            responsaveis=item.responsaveis,
                            comunicar_inicio=item.comunicar_inicio,
                            comunicar_termino=item.comunicar_termino,
                            recursos=item.recursos,
                        )
                    )
                self.calcula_datas(cronograma_list)
                for item in cronograma_list:
                    item.save()
            elif self.cronograma_set.count() > 0:
                cronograma_list = self.cronograma_set.all()
                self.calcula_datas(cronograma_list)
                for item in cronograma_list:
                    item.save()
        super().save(*args, **kwargs)

    def calcula_datas(self, cronograma_list):
        def ajusta_data(elemento, data_termino):
            if (
                elemento.data_prevista_termino is None
                or elemento.data_prevista_termino > data_termino
            ):
                elemento.data_prevista_termino = data_termino
            elemento.data_prevista_inicio = (
                elemento.data_prevista_termino
                - datetime.timedelta(days=elemento.duracao - 1)
            )
            for item in cronograma_list:
                if item.etapa in elemento.dependencia:
                    ajusta_data(
                        item,
                        elemento.data_prevista_inicio
                        - datetime.timedelta(days=1),
                    )

        leafs = [
            item
            for item in cronograma_list
            if len([d for d in cronograma_list if item.etapa in d.dependencia])
            == 0
        ]
        for item in leafs:
            ajusta_data(item, self.data_termino.date())


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
    TIPO_AULA = "A"
    TIPO_PALESTRA = "P"
    TIPO_APRESENTACAO = "R"

    TIPO_CHOICES = (
        (TIPO_AULA, _("Aula")),
        (TIPO_PALESTRA, _("Palestra")),
        (TIPO_APRESENTACAO, _("Apresentação")),
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


class Checklist(models.Model):
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.CASCADE)
    etapa = models.CharField(_("sigla da etapa"), max_length=10)
    nome = models.CharField(_("nome da etapa"), max_length=100)
    descricao = models.TextField(
        _("descrição da etapa"),
        help_text=_("Descrição detalhada das atividades realizadas na etapa"),
    )
    duracao = models.PositiveBigIntegerField(_("duração (em dias)"))
    dependencia = models.CharField(
        _("depende da etapa"),
        max_length=200,
        help_text=_(
            "Siglas das etapas que precisam ser concluídas para que esta seja iniciada. Separe cada uma com um espaço."
        ),
        blank=True,
    )
    responsaveis = models.TextField(
        _("responsáveis pela tarefa"),
        help_text=_("Pessoas, setores, órgãos."),
        blank=True,
    )
    comunicar_inicio = models.TextField(
        _("comunicar inicio para"),
        help_text=_(
            "Lista de e-mails para comunicar quando a tarefa for iniciada"
        ),
        blank=True,
    )
    comunicar_termino = models.TextField(
        _("comunicar término para"),
        help_text=_(
            "Lista de e-mails para comunicar quando a tarefa for concluída"
        ),
        blank=True,
    )
    recursos = models.TextField(
        _("recursos necessários"),
        help_text="Lista de recursos necessários para desenvolver a tarefa",
    )

    class Meta:
        verbose_name = _("checklist")
        verbose_name_plural = _("checklists")

    def __str__(self):
        return _(f"{self.etapa}: {self.nome}")


class Cronograma(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    etapa = models.CharField(_("sigla da etapa"), max_length=10)
    nome = models.CharField(_("nome da etapa"), max_length=100)
    descricao = models.TextField(
        _("descrição da etapa"),
        help_text=_("Descrição detalhada das atividades realizadas na etapa"),
    )
    duracao = models.PositiveBigIntegerField(_("duração (em dias)"))
    data_prevista_inicio = models.DateField(
        _("data prevista de início"), blank=True, null=True
    )
    data_prevista_termino = models.DateField(
        _("data prevista de término"), blank=True, null=True
    )
    data_inicio = models.DateField(_("data de início"), blank=True, null=True)
    data_termino = models.DateField(_("data de término"), blank=True, null=True)
    dependencia = models.CharField(
        _("depende da etapa"),
        max_length=200,
        help_text=_(
            "Sigla da etapa que precisa ser concluída para que esta seja iniciada"
        ),
        blank=True,
    )
    responsaveis = models.TextField(
        _("responsáveis pela tarefa"),
        help_text=_("Pessoas, setores, órgãos."),
        blank=True,
    )
    comunicar_inicio = models.TextField(
        _("comunicar inicio para"),
        help_text=_(
            "Lista de pessoas/órgãos para comunicar quando a tarefa for iniciada. Coloque um por linha."
        ),
        blank=True,
    )
    comunicar_termino = models.TextField(
        _("comunicar término para"),
        help_text=_(
            "Lista de pessoas/órgãos para comunicar quando a tarefa for concluída. Coloque um por linha."
        ),
        blank=True,
    )
    recursos = models.TextField(
        _("recursos necessários"),
        help_text="Lista de recursos necessários para desenvolver a tarefa",
    )

    class Meta:
        verbose_name = _("cronograma")
        verbose_name_plural = _("cronogramas")

    def __str__(self):
        return _(f"{self.etapa}: {self.nome}")

    def get_dependencias(self):
        return self.evento.cronograma_set.filter(
            etapa__in=self.dependencia.split(" ")
        )

    def get_dependentes(self):
        return self.evento.cronograma_set.filter(
            dependencia__icontains=self.etapa
        )
