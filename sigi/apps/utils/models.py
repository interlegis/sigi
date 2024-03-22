import io
from contextlib import redirect_stderr, redirect_stdout
from cron_converter import Cron
from pyexpat import model
from django.db import models
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.formats import localize
from django.utils.translation import gettext as _
from django_extensions.management.jobs import get_job, get_jobs
from tinymce.models import HTMLField


class SigiAlert(models.Model):
    DESTINATARIOS_CHOICES = (
        ("A", _("Todo e qualquer usuário")),
        ("N", _("Usuários anônimos / não autenticados")),
        ("S", _("Membros da equipe Interlegis")),
        ("D", _("Administradores do sistema")),
    )
    caminho = models.CharField(_("caminho da tela"), max_length=200)
    destinatarios = models.CharField(
        _("destinatários"), max_length=1, choices=DESTINATARIOS_CHOICES
    )
    titulo = models.CharField(_("título"), max_length=60)
    mensagem = HTMLField(_("mensagem"))

    class Meta:
        ordering = ("caminho", "destinatarios")
        verbose_name = _("alerta SIGI")
        verbose_name_plural = _("alertas SIGI")

    def __str__(self):
        return self.titulo


class Cronjob(models.Model):
    app_name = models.CharField(_("app"), max_length=100, editable=False)
    job_name = models.CharField(_("job"), max_length=100, editable=False)
    expressao_cron = models.CharField(
        _("expressão CRON"),
        max_length=100,
        default="* * * * *",
        help_text=_(
            "Usar expressoões no formato padrão de CRON: "
            "'minute hour day month day-of-week'. "
            "Mais detalhes: "
            "<a href='https://help.ubuntu.com/community/CronHowto'>"
            "CronHowTo"
            "</a>"
        ),
    )

    class Meta:
        ordering = ("app_name", "job_name")
        verbose_name = _("Cron job")
        verbose_name_plural = _("Cron jobs")

    def __str__(self):
        return self.job_name

    def run(self):
        try:
            JobClass = get_job(self.app_name, self.job_name)
        except KeyError:
            return (
                f"A rotina de JOB {self.job.job_name} do app "
                f"{self.job.app_name} não foi encontrada."
            )
        try:
            job_obj = JobClass()
            with io.StringIO() as so_buf, io.StringIO() as se_buf, redirect_stdout(
                so_buf
            ), redirect_stderr(
                se_buf
            ):
                job_obj.execute()
                messages = so_buf.getvalue()
                errors = se_buf.getvalue()
            report_data = ["", "MENSAGENS", "---------", ""]
            if messages:
                report_data.extend(messages.splitlines())
            else:
                report_data.extend(["Nenhuma mensagem gerada", ""])
            report_data.extend(["", "ERROS", "-----", ""])
            if errors:
                report_data.extend(errors.splitlines())
            else:
                report_data.extend(["Nenhum erro gerado", ""])
            return "\n".join(report_data)
        except Exception as e:
            # Qualquer erro deve ser reportado
            return _(f"JOB abortado com erro: {str(e)}")

    def next_schedule(self):
        """Recupera a agenda da próxima execução. Se não existe, cria."""
        try:
            sch = self.jobschedule_set.get(
                status__in=[
                    JobSchedule.STATUS_AGENDADO,
                    JobSchedule.STATUS_EXECUTANDO,
                ]
            )
        except JobSchedule.DoesNotExist:
            iniciar = self.get_next_schedule_time()
            sch = JobSchedule(job=self, iniciar=iniciar)
            sch.save()
        return sch

    def get_next_schedule_time(self):
        cron_instance = Cron(self.expressao_cron)
        scheduller = cron_instance.schedule(timezone.localtime())
        return scheduller.next()


class JobSchedule(models.Model):
    STATUS_AGENDADO = "A"
    STATUS_EXECUTANDO = "E"
    STATUS_CONCLUIDO = "C"
    STATUS_CHOICES = (
        (STATUS_AGENDADO, _("Agendado")),
        (STATUS_EXECUTANDO, _("Executando")),
        (STATUS_CONCLUIDO, _("Concluído")),
    )
    job = models.ForeignKey(
        Cronjob, verbose_name=_("Cron job"), on_delete=models.CASCADE
    )
    iniciar = models.DateTimeField(_("Iniciar em"))
    iniciado = models.DateTimeField(_("Iniciado em"), blank=True, null=True)
    status = models.CharField(
        _("estado"),
        max_length=1,
        choices=STATUS_CHOICES,
        default=STATUS_AGENDADO,
    )
    tempo_gasto = models.DurationField(
        _("tempo gasto"), blank=True, null=True, editable=False
    )
    resultado = models.TextField(
        _("resultado da execução"), blank=True, editable=False
    )

    class Meta:
        ordering = ("iniciar",)
        verbose_name = _("Agenda de execução")
        verbose_name_plural = _("Agenda de execuções")

    class DoesNotExecute(Exception):
        """This scheduled job cannot be executed because not in AGENDADO state"""

        pass

    def __str__(self):
        if self.status == JobSchedule.STATUS_AGENDADO:
            return _(
                f"{self.job.job_name}: início agendado para "
                f"{localize(timezone.localtime(self.iniciar))}."
            )
        elif self.status == JobSchedule.STATUS_EXECUTANDO:
            return _(
                f"{self.job.job_name}: em execução desde "
                f"{localize(timezone.localtime(self.iniciado))}"
            )
        return _(
            f"{self.job.job_name}: executado em "
            f"{localize(timezone.localtime(self.iniciado))}, "
            f"levando {self.tempo_gasto} para concluir"
        )

    def run_job(self):
        """Executa o job agendado. Esta rotina não verifica se a agenda está
        na hora certa, apenas executa o job associado."""

        if self.status != JobSchedule.STATUS_AGENDADO:
            raise JobSchedule.DoesNotExecute()

        self.iniciado = timezone.localtime()
        self.status = JobSchedule.STATUS_EXECUTANDO
        self.save()
        self.resultado = self.job.run()
        self.status = JobSchedule.STATUS_CONCLUIDO
        self.tempo_gasto = timezone.localtime() - self.iniciado
        self.save()


class Config(models.Model):
    PARAMETRO_CHOICES = (
        ("ENCERRA_INSCRICAO", _("Encerra inscrições de oficinas no Portal")),
        ("EMAIL_JOBS", _("E-mail de jobs")),
    )
    DEFAULTS = {
        "ENCERRA_INSCRICAO": "30",
        "EMAIL_JOBS": "sigi@interlegis.leg.br",
    }
    parametro = models.CharField(
        _("parâmetro"), max_length=100, choices=PARAMETRO_CHOICES
    )
    valor = models.CharField(_("valor do parâmettro"), max_length=200)

    class Meta:
        ordering = ("parametro",)
        verbose_name = _("Parâmetro de configuração")
        verbose_name_plural = _("Parâmetros de configuração")

    def __str__(self):
        return f"{self.get_parametro_display()}: {self.valor}"

    @classmethod
    def get_param(cls, parametro):
        if parametro not in cls.DEFAULTS:
            raise cls.DoesNotExist(
                _(
                    f"Não existe o parâmetro '{parametro}'. "
                    f"As opções são {', '.join(cls.DEFAULTS.keys())}."
                )
            )
        valores = list(
            cls.objects.filter(parametro=parametro).values_list(
                "valor", flat=True
            )
        )
        if not valores:
            valores.append(cls.DEFAULTS[parametro])
        return valores
