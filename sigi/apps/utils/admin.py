from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, path
from django.utils import timezone
from django.utils.formats import localize
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_extensions.management.jobs import get_job, get_jobs
from tinymce.models import HTMLField
from tinymce.widgets import AdminTinyMCE
from sigi.apps.utils.models import SigiAlert, Cronjob, JobSchedule, Config


class JobScheduleInline(admin.TabularInline):
    model = JobSchedule
    fields = ["status", "iniciar", "iniciado", "tempo_gasto", "get_runner"]
    readonly_fields = [
        "status",
        "iniciar",
        "iniciado",
        "tempo_gasto",
        "get_runner",
    ]
    can_delete = False
    can_add = False
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    @mark_safe
    @admin.display(description=_("Ver/executar"))
    def get_runner(self, sched):
        if sched.status == JobSchedule.STATUS_AGENDADO:
            url = reverse("admin:utils_jobschedule_runjob", args=[sched.id])
            return (
                f"<a href='{url}' title='{_('Executar')}'>"
                "<i class='material-icons'>play_arrow</i></a>"
            )
        elif sched.status == JobSchedule.STATUS_CONCLUIDO:
            url = reverse("admin:utils_jobschedule_change", args=[sched.id])
            return (
                f"<a href='{url}' title='{_('Ver resultado')}'>"
                "<i class='material-icons'>description</i></a>"
            )
        return ""


@admin.register(SigiAlert)
class SigiAlertAdmin(admin.ModelAdmin):
    list_display = ("titulo", "caminho", "destinatarios")
    search_fields = ("titulo", "caminho")
    formfield_overrides = {HTMLField: {"widget": AdminTinyMCE}}
    list_filter = ("destinatarios",)


@admin.register(Cronjob)
class CronjobAdmin(admin.ModelAdmin):
    list_display = (
        "job_name",
        "app_name",
        "get_help",
        "expressao_cron",
        "get_schedule",
        "get_runner",
        "destinatario_email",
        "digest",
        "last_digest",
    )
    fields = [
        "job_name",
        "app_name",
        "get_help",
        "expressao_cron",
        "manter_logs",
        "destinatario_email",
        "digest",
        "last_digest",
    ]
    readonly_fields = ("job_name", "app_name", "get_help")
    inlines = [JobScheduleInline]

    def get_urls(self):
        urls = super().get_urls()
        model_info = (self.model._meta.app_label, self.model._meta.model_name)

        my_urls = [
            path(
                "<path:object_id>/runjob/",
                self.admin_site.admin_view(self.run_job),
                name="%s_%s_runjob" % model_info,
            ),
        ]
        return my_urls + urls

    @admin.display(description=_("descrição"))
    def get_help(self, job):
        try:
            JobClass = get_job(job.app_name, job.job_name)
        except KeyError:
            return _(
                f"A rotina de JOB {job.app_name}.{job.job_name} "
                "não foi encontrada."
            )
        job_obj = JobClass()
        return job_obj.help

    @admin.display(description=_("agenda"))
    def get_schedule(self, job):
        sched = job.jobschedule_set.first()
        if sched is None:
            return _("Nenhum agendamento para este job")
        if sched.status == JobSchedule.STATUS_AGENDADO:
            return _(
                "início agendado para "
                f"{localize(timezone.localtime(sched.iniciar))}."
            )
        if sched.status == JobSchedule.STATUS_EXECUTANDO:
            return _(
                "em execução desde "
                f"{localize(timezone.localtime(sched.iniciado))}"
            )
        return _(
            f"executado em {localize(timezone.localtime(sched.iniciado))}, "
            f"levando {sched.tempo_gasto} minutos para concluir"
        )

    @mark_safe
    @admin.display(description=_("executar"))
    def get_runner(self, job):
        url = reverse("admin:utils_cronjob_runjob", args=[job.id])
        return (
            f"<a href='{url}'>" "<i class='material-icons'>play_arrow</i></a>"
        )

    def run_job(self, request, object_id):
        cronjob = get_object_or_404(Cronjob, id=object_id)
        sched = cronjob.next_schedule()
        if sched.status != JobSchedule.STATUS_AGENDADO:
            raise PermissionDenied(
                _(
                    "Este agendamento não pode ser executado pois "
                    f"está com status {sched.get_status_display()}"
                )
            )
        sched.run_job()
        self.message_user(
            request,
            _("JOB executado!"),
            messages.SUCCESS,
        )
        return redirect("admin:utils_jobschedule_change", object_id=sched.id)


@admin.register(JobSchedule)
class JobScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "job",
        "status",
        "iniciar",
        "iniciado",
        "tempo_gasto",
        "get_runner",
    ]
    fields = [
        "job",
        "status",
        "iniciar",
        "iniciado",
        "tempo_gasto",
    ]
    readonly_fields = fields
    list_filter = ("status", "job")
    date_hierarchy = "iniciar"

    def get_urls(self):
        urls = super().get_urls()
        model_info = (self.model._meta.app_label, self.model._meta.model_name)

        my_urls = [
            path(
                "<path:object_id>/runjob/",
                self.admin_site.admin_view(self.run_job),
                name="%s_%s_runjob" % model_info,
            ),
        ]
        return my_urls + urls

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if obj is None or obj.status == JobSchedule.STATUS_CONCLUIDO:
            return super().has_delete_permission(request, obj)
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return False

    @mark_safe
    @admin.display(description=_("executar"))
    def get_runner(self, sched):
        if sched.status == JobSchedule.STATUS_AGENDADO:
            url = reverse("admin:utils_jobschedule_runjob", args=[sched.id])
            return (
                f"<a href='{url}'>"
                "<i class='material-icons'>play_arrow</i></a>"
            )
        return ""

    def run_job(self, request, object_id):
        sched = get_object_or_404(JobSchedule, id=object_id)
        if sched.status != JobSchedule.STATUS_AGENDADO:
            raise PermissionDenied(
                _(
                    "Este agendamento não pode ser executado pois "
                    f"está com status {sched.get_status_display()}"
                )
            )
        sched.run_job()
        self.message_user(
            request,
            _("JOB executado!"),
            messages.SUCCESS,
        )
        return redirect("admin:utils_jobschedule_change", object_id=object_id)


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ["parametro", "valor"]
    list_filter = ["parametro"]
