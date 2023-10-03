from collections.abc import Iterable
import datetime
import re
from moodle import Moodle
from tinymce.models import HTMLField
from django.conf import settings
from django.contrib import admin
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Count, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from sigi.apps.casas.models import Orgao, Servidor
from sigi.apps.contatos.models import Municipio
from sigi.apps.servidores.models import Servidor


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
    sigla = models.CharField(_("sigla"), max_length=20, blank=True)
    categoria = models.CharField(
        _("Categoria"), max_length=1, choices=CATEGORIA_CHOICES
    )
    casa_solicita = models.BooleanField(
        _("casa pode solicitar"), default=False
    )
    gerar_turma = models.BooleanField(
        _("Gerar turma"),
        default=True,
        help_text=_(
            "Se o campo 'turma' for deixado em branco, o sistema deve gerar "
            "um número de turma automaticamente, com base no ano da data de "
            "início do evento?"
        ),
    )
    duracao = models.PositiveIntegerField(_("Duração (dias)"), default=1)
    moodle_template_courseid = models.PositiveBigIntegerField(
        _("Curso protótipo"),
        blank=True,
        null=True,
        help_text=_(
            "Código do curso que serve de protótipo no Saberes para criação de "
            "novos eventos desse tipo."
        ),
    )
    moodle_categoryid = models.PositiveBigIntegerField(
        _("Categoria do curso"),
        blank=True,
        null=True,
        help_text=_(
            "Código da categoria no Saberes onde o curso deve ser criado."
        ),
    )
    prefixo_turma = models.CharField(
        _("Prefixo para turmas"), max_length=20, blank=True
    )

    class Meta:
        ordering = ("nome",)
        verbose_name, verbose_name_plural = _("Tipo de evento"), _(
            "Tipos de evento"
        )

    def __str__(self):
        return self.nome


class Solicitacao(models.Model):
    STATUS_SOLICITADO = "S"
    STATUS_AUTORIZADO = "A"
    STATUS_REJEITADO = "R"
    STATUS_CONCLUIDO = "C"
    STATUS_CHOICES = (
        (STATUS_SOLICITADO, _("Solicitado")),
        (STATUS_AUTORIZADO, _("Autorizado")),
        (STATUS_REJEITADO, _("Rejeitado")),
        (STATUS_CONCLUIDO, _("Concluído")),
    )
    casa = models.ForeignKey(
        Orgao, verbose_name=_("casa solicitante"), on_delete=models.PROTECT
    )
    senador = models.CharField(_("senador(a) solicitante"), max_length=100)
    num_processo = models.CharField(
        _("número do processo SIGAD"),
        max_length=20,
        blank=True,
        help_text=_("Formato:<em>XXXXX.XXXXXX/XXXX-XX</em>"),
    )
    descricao = models.TextField(_("descrição da solicitação"))
    data_pedido = models.DateField(
        _("Data do pedido"),
        help_text=_("Data em que o pedido foi realizado"),
    )
    data_recebido_coperi = models.DateField(
        _("data de recebimento na COPERI"),
        null=True,
        blank=True,
        help_text=_("Data em que o pedido chegou na COPERI"),
    )
    status = models.CharField(
        _("Status"),
        max_length=1,
        choices=STATUS_CHOICES,
        default=STATUS_SOLICITADO,
    )
    servidor = models.ForeignKey(
        Servidor,
        verbose_name=_("servidor analisador"),
        help_text=_(
            "Servidor que autorizou ou rejeitou a realização do evento"
        ),
        on_delete=models.PROTECT,
        limit_choices_to={"externo": False},
        blank=True,
        null=True,
        editable=False,
    )
    data_analise = models.DateTimeField(
        _("data de autorização/rejeição"),
        blank=True,
        null=True,
        editable=False,
    )
    justificativa = models.TextField(
        verbose_name=_("Justificativa"), blank=True
    )
    contato = models.CharField(
        _("pessoa de contato na Casa"), max_length=100, blank=True
    )
    email_contato = models.EmailField(_("e-mail do contato"), blank=True)
    telefone_contato = models.CharField(
        _("telefone do contato"), max_length=20, blank=True
    )
    whatsapp_contato = models.CharField(
        _("whatsapp do contato"), max_length=20, blank=True
    )
    estimativa_casas = models.PositiveIntegerField(
        _("estimativa de Casas participantes"),
        help_text=_("estimativa de quantas Casas participarão dos eventos"),
        default=0,
    )
    estimativa_servidores = models.PositiveIntegerField(
        _("estimativa de servidores participantes"),
        help_text=_(
            "estimativa de quantos Servidores participarão dos eventos"
        ),
        default=0,
    )

    class Meta:
        ordering = ("-data_pedido",)
        verbose_name = _("Solicitação de eventos")
        verbose_name_plural = _("Solicitações de eventos")

    def __str__(self):
        return _(f"{self.num_processo}: {self.casa} / Senador {self.senador}")

    @admin.display(description=_("SIGAD"), ordering="num_processo")
    def get_sigad_url(self):
        m = re.match(
            "(?P<orgao>00100|00200)\.(?P<sequencial>\d{6})/(?P<ano>"
            "\d{4})-\d{2}",
            self.num_processo,
        )
        if m:
            return mark_safe(
                (
                    '<a href="https://intra.senado.leg.br/'
                    "sigad/novo/protocolo/impressao.asp?area=processo"
                    "&txt_numero_orgao={orgao}"
                    "&txt_numero_sequencial={sequencial}"
                    '&txt_numero_ano={ano}"'
                    ' target="_blank">{processo}</a>'
                ).format(processo=self.num_processo, **m.groupdict())
            )
        return self.num_processo

    @admin.display(description=_("Oficinas atendidas/confirmadas na UF"))
    def get_oficinas_uf(self):
        ano_corrente = timezone.localdate().year
        counters = Evento.objects.filter(
            status__in=[Evento.STATUS_CONFIRMADO, Evento.STATUS_REALIZADO],
            casa_anfitria__municipio__uf=self.casa.municipio.uf,
            tipo_evento__categoria=TipoEvento.CATEGORIA_OFICINA,
        ).aggregate(
            total=Count("id"),
            no_ano=Count("id", filter=Q(data_inicio__year=ano_corrente)),
            dois_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 1),
            ),
            tres_anos=Count(
                "id",
                filter=Q(data_inicio__year__gte=ano_corrente - 2),
            ),
        )
        return _(
            (
                "Total: {total}, no ano corrente: {no_ano}, "
                "nos dois últimos anos: {dois_anos}, "
                "nos três últimos anos: {tres_anos}"
            ).format(**counters)
        )


class ItemSolicitado(models.Model):
    STATUS_SOLICITADO = "S"
    STATUS_AUTORIZADO = "A"
    STATUS_REJEITADO = "R"
    STATUS_CHOICES = (
        (STATUS_SOLICITADO, _("Solicitado")),
        (STATUS_AUTORIZADO, _("Autorizado")),
        (STATUS_REJEITADO, _("Rejeitado")),
    )
    solicitacao = models.ForeignKey(Solicitacao, on_delete=models.CASCADE)
    tipo_evento = models.ForeignKey(
        TipoEvento,
        on_delete=models.PROTECT,
    )
    virtual = models.BooleanField(_("virtual"), default=False)
    inicio_desejado = models.DateField(
        _("início desejado"),
        help_text=_(
            "Data desejada para o início do evento. Pode ser solicitado pela Casa ou definido pela conveniência do Interlegis. Será usada como data de início do evento, caso seja autorizado."
        ),
    )
    status = models.CharField(
        verbose_name=_("status"),
        choices=STATUS_CHOICES,
        default=STATUS_SOLICITADO,
    )
    data_analise = models.DateTimeField(
        _("data da autorização/rejeição"),
        blank=True,
        null=True,
        editable=False,
    )
    servidor = models.ForeignKey(
        Servidor,
        verbose_name=_("servidor analisador"),
        help_text=_(
            "Servidor que autorizou ou rejeitou a realização do evento"
        ),
        on_delete=models.PROTECT,
        limit_choices_to={"externo": False},
        blank=True,
        null=True,
        editable=False,
    )
    data_analise = models.DateTimeField(
        _("data de autorização/rejeição"),
        blank=True,
        null=True,
        editable=False,
    )
    justificativa = models.TextField(
        verbose_name=_("Justificativa"), blank=True
    )
    evento = models.ForeignKey(
        "Evento", on_delete=models.SET_NULL, null=True, editable=False
    )

    class Meta:
        ordering = ("status",)
        verbose_name = _("Evento solicitado")
        verbose_name_plural = _("Eventos solicitados")

    def __str__(self):
        return _(f"{self.tipo_evento}: {self.get_status_display()}")


class AnexoSolicitacao(models.Model):
    solicitacao = models.ForeignKey(
        Solicitacao, on_delete=models.CASCADE, verbose_name=_("evento")
    )
    arquivo = models.FileField(
        upload_to="apps/eventos/solicitacao/anexo/arquivo", max_length=500
    )
    descricao = models.CharField(_("descrição"), max_length=70)
    data_pub = models.DateTimeField(
        _("data da publicação do anexo"), default=timezone.localtime
    )

    class Meta:
        ordering = ("-data_pub",)
        verbose_name = _("Anexo")
        verbose_name_plural = _("Anexos")

    def __str__(self):
        return _(f"{self.descricao} publicado em {self.data_pub}")


class Evento(models.Model):
    class SaberesSyncException(Exception):
        @property
        def message(self):
            return str(self)

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
    turma = models.CharField(
        _("turma"),
        max_length=100,
        blank=True,
        validators=[
            RegexValidator(
                "^\d{2}/\d{4}$",
                _(
                    "Formato inválido. Utilize nn/aaaa, onde 'nn' são dígitos "
                    "numéricos e 'aaaa' o ano com quatro dígitos."
                ),
            )
        ],
        help_text=_(
            "Se deixado em branco e o evento tiver status CONFIRMADO e "
            "data de início definida, o número da turma será "
            "gerado automaticamente."
        ),
    )
    descricao = models.TextField(
        _("Descrição do evento"),
        default=_(
            "solicitar Acordo de Cooperação Técnica entre a Câmara Municipal "
            "e esta Escola de Governo do Senado Federal. Na ocasião foram "
            "apresentados os produtos e serviços oferecidos gratuitamente pelo "
            "Programa Interlegis"
        ),
    )
    virtual = models.BooleanField(_("Virtual"), default=False)
    solicitante = models.CharField(_("senador(a) solicitante"), max_length=100)
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
        help_text=_("Data em que o pedido foi realizado"),
    )
    data_recebido_coperi = models.DateField(
        _("data de recebimento na COPERI"),
        null=True,
        blank=True,
        help_text=_("Data em que o pedido chegou na COPERI"),
    )
    solicitacao = models.ForeignKey(
        "ocorrencias.Ocorrencia",
        blank=True,
        null=True,
        verbose_name=_("Solicitação de origem"),
        on_delete=models.SET_NULL,
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
    local = models.TextField(_("Local do evento"), blank=True)
    observacao = models.TextField(_("Observações e anotações"), blank=True)
    publico_alvo = models.TextField(_("Público alvo"), blank=True)
    total_participantes = models.PositiveIntegerField(
        _("total de participantes/aprovados"),
        default=0,
        help_text=_(
            "Se existe evento relacionado no saberes, mostra o número de "
            "participantes aprovados naquela plataforma. Senão, mostra a "
            "somatória de participantes das Casas convidadas ou o número "
            "de participantes informado manualmente pelo usuário."
        ),
    )
    inscritos_saberes = models.PositiveIntegerField(
        _("inscritos no Saberes"),
        default=0,
        help_text=_(
            "Número de pessoas que se inscreveram no evento no Saberes. "
            "Computado via integração SIGI x Saberes."
        ),
        editable=False,
    )
    aprovados_saberes = models.PositiveIntegerField(
        _("aprovados no Saberes"),
        default=0,
        help_text=_(
            "Número de pessoas que concluíram o curso no Saberes. "
            "Computado via integração SIGI x Saberes."
        ),
        editable=False,
    )
    data_sincronizacao = models.DateTimeField(
        _("data da última sincronização com Saberes"),
        null=True,
        editable=False,
    )
    status = models.CharField(
        _("Status"), max_length=1, choices=STATUS_CHOICES
    )
    publicar = models.BooleanField(_("publicar no site"), default=False)
    moodle_courseid = models.PositiveBigIntegerField(
        _("ID do curso"),
        blank=True,
        null=True,
        help_text=_(
            "ID do curso no Saberes. Este campo é preenchido automaticamente "
            "quando o curso é criado no Saberes."
        ),
    )
    chave_inscricao = models.CharField(
        _("chave de inscrição"), max_length=100, blank=True
    )
    perfil_aluno = models.URLField(
        _("Link do perfil do aluno"),
        blank=True,
        help_text=_(
            "Link completo da página de perfil do aluno deste curso no Saberes"
        ),
    )
    observacao_inscricao = models.TextField(
        _("Observações para inscrição"),
        blank=True,
        default=_(
            "Passo a passo para a inscrição:<BR>"
            "1. Acesse a plataforma Saberes para ir direto ao curso.<BR>"
            "2. Para efetivar a matrícula, insira a CHAVE DE INSCRIÇÃO "
            "indicada acima.<BR>"
            "3. Dentro da plataforma Saberes, preencha o PERFIL DO ESTUDANTE "
            "e junte-se ao grupo do Whatsapp para receber informações.<BR>"
            "4. No dia da Oficina, leve seu notebook com mouse, "
            "se possível.<BR>"
            "ATENÇÃO: as inscrições ficarão abertas até o dia anterior ao "
            "início da Oficina (14h), ou até atingir o número máximo de "
            "participantes."
        ),
        help_text=_(
            "Mais detalhes para ajudar o aluno a se inscrever no curso"
        ),
    )
    contato_inscricao = models.CharField(
        _("contato para inscrição"),
        max_length=100,
        blank=True,
        default=_("Central de Atendimento - Oficinas."),
        help_text=_(
            "pessoa ou setor responsável por dar suporte aos alunos no "
            "processo de inscrição"
        ),
    )
    telefone_inscricao = models.CharField(
        _("telefone do contato"),
        max_length=60,
        blank=True,
        default=_("(61)3303-2026 ; (61)99862-7973 (zap)"),
        help_text=_(
            "telefone da pessoa ou setor responsável por dar suporte aos "
            "alunos no processo de inscrição"
        ),
    )
    contato = models.CharField(
        _("contato"),
        max_length=100,
        blank=True,
        help_text=_("pessoa de contato na casa anfitriã"),
    )
    telefone = models.CharField(
        _("tefone de contato"),
        max_length=30,
        blank=True,
        help_text=_("telefone da pessoa de contato na casa anfitriã"),
    )
    banner = models.ImageField(
        _("banner do evento"),
        blank=True,
        upload_to="apps/eventos/evento/banner/",
    )
    data_cancelamento = models.DateField(
        _("Data de cancelamento"), blank=True, null=True
    )
    motivo_cancelamento = models.TextField(
        _("Motivo do cancelamento"), blank=True
    )

    class Meta:
        ordering = ("-data_inicio",)
        verbose_name, verbose_name_plural = _("Evento"), _("Eventos")
        permissions = [
            ("createcourse_evento", "Can create courses in Saberes platform"),
        ]

    def __str__(self):
        return _(
            f"{self.nome} ({self.tipo_evento}): "
            f"de {self.data_inicio} a {self.data_termino}"
        )

    def get_absolute_url(self):
        return reverse("admin:eventos_evento_change", args=[self.id])

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

    @property
    def link_inscricao(self):
        if self.moodle_courseid is None:
            return ""
        from django.conf import settings

        return (
            settings.MOODLE_BASE_URL
            + f"/course/view.php?id={self.moodle_courseid}"
        )

    def sincroniza_saberes(self):
        if self.moodle_courseid is None:
            raise Evento.SaberesSyncException(
                _("Este evento não tem curso associado no Saberes"),
            )

        api_url = f"{settings.MOODLE_BASE_URL}/webservice/rest/server.php"
        mws = Moodle(api_url, settings.MOODLE_API_TOKEN)
        try:
            inscritos = mws.post(
                "core_enrol_get_enrolled_users",
                courseid=self.moodle_courseid,
            )
        except Exception as e:
            raise Evento.SaberesSyncException(
                _(
                    "Ocorreu um erro ao acessar o curso no Saberes com "
                    f"a mensagem {e.message}"
                ),
            )
        participantes = list(
            filter(
                lambda u: any(
                    r["roleid"] in settings.MOODLE_STUDENT_ROLES
                    for r in u["roles"]
                ),
                inscritos,
            )
        )

        aprovados = 0
        for participante in participantes:
            try:
                completion_data = mws.post(
                    "core_completion_get_course_completion_status",
                    courseid=self.moodle_courseid,
                    userid=participante["id"],
                )
            except Exception:
                completion_data = None

            if completion_data and (
                completion_data["completionstatus"]["completed"]
                or any(
                    filter(
                        lambda c: c["type"]
                        == settings.MOODLE_COMPLETE_CRITERIA_TYPE
                        and c["complete"],
                        completion_data["completionstatus"]["completions"],
                    )
                )
            ):
                aprovados += 1

        self.inscritos_saberes = len(participantes)
        self.aprovados_saberes = aprovados
        self.data_sincronizacao = timezone.localtime()

        # O total de participantes em eventos que possuem curso no Saberes
        # é sempre o número de aprovados no Saberes, independente do que o
        # usuário tenha digitado nesse campo ou no inline de casas convidadas
        self.total_participantes = self.aprovados_saberes

        self.save()

    def save(self, *args, **kwargs):
        if self.status != Evento.STATUS_CANCELADO:
            self.data_cancelamento = None
            self.motivo_cancelamento = ""
        if (
            self.data_inicio
            and self.data_termino
            and self.data_inicio > self.data_termino
        ):
            raise ValidationError(
                _("Data de término deve ser posterior à data de início")
            )

        if (
            self.turma == ""
            and self.data_inicio
            and self.status == Evento.STATUS_CONFIRMADO
            and self.tipo_evento.gerar_turma
        ):
            ano = self.data_inicio.year
            ultimo_evento = (
                Evento.objects.filter(
                    tipo_evento=self.tipo_evento,
                    turma__regex=f"\d{{2}}/{ano:04}$",
                )
                .order_by("turma")
                .last()
            )
            if ultimo_evento is None:
                proximo = 1
            else:
                proximo = int(ultimo_evento.turma[:2]) + 1
            self.turma = f"{proximo:02}/{ano:04}"

        # É preciso salvar para poder usar o relacionamento com convites
        super().save(*args, **kwargs)

        if self.total_participantes == 0 and self.moodle_courseid is None:
            # Só calcula total_participantes se não tem curso relacionado
            # no ambiente Saberes. Se tiver curso no saberes, este campo será
            # preenchido com o total de aprovados quando da sincronização
            # veja o método self.sincroniza.saberes()

            total = self.convite_set.aggregate(
                total=Sum("qtde_participantes")
            )["total"]
            if total and total > 0 and total != self.total_participantes:
                self.total_participantes = total
                # Salva de novo se o total de participantes mudou #
                super().save(*args, **kwargs)

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
    moodle_roleid = models.PositiveBigIntegerField(
        _("Papel Saberes"),
        blank=True,
        null=True,
        help_text=_("Código do papel do membro da equipe no Saberes"),
    )

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
    qtde_participantes = models.PositiveIntegerField(
        _("número de participantes"), default=0
    )
    nomes_participantes = models.TextField(
        _("nome dos participantes"),
        blank=True,
        help_text=_("Favor colocar um participante por linha"),
    )

    class Meta:
        ordering = ("evento", "casa")
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
    data_termino = models.DateField(
        _("data de término"), blank=True, null=True
    )
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
