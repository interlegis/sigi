from django_extensions.management.jobs import BaseJob
from django_extensions.management.jobs import get_jobs
from django.utils import timezone
from django.utils.formats import localize
from django.utils.translation import gettext as _
from sigi.apps.utils.models import Cronjob, JobSchedule

WHEN_SETS = {
    "daily": "0 0 * * *",
    "hourly": "0 * * * *",
    "monthly": "0 0 1 * *",
    "weekly": "0 0 * * 0",
    "yearly": "0 0 1 1 *",
    "minutely": "* * * * *",
}


class Job(BaseJob):
    help = "Controlador de cronjobs do SIGI."

    def execute(self):
        print("Rodando controlador de jobs...")
        self.remove_old_jobs()
        self.sync_new_jobs()
        self.run_scheduled()
        self.schedule_jobs()
        self.remove_old_logs()

    def remove_old_jobs(self):
        """Remover das tabelas os jobs que foram removidos do código"""
        print("\tRemover das tabelas os jobs que foram removidos do código...")
        all_jobs = get_jobs()
        excludes = Cronjob.objects.all()
        for app_name, job_name in all_jobs.keys():
            excludes = excludes.exclude(app_name=app_name, job_name=job_name)
        print("\t\t", excludes.delete())

    def sync_new_jobs(self):
        """
        Atualizar a tabela de JOBS com os novos JOBS que tenham sido criados
        """
        print(
            "\tAtualizar a tabela de JOBS com os novos JOBS que tenham "
            "sido criados..."
        )
        all_jobs = get_jobs()
        for (app_name, job_name), JobClass in all_jobs.items():
            if app_name == "sigi.apps.utils" and job_name == "job_controller":
                # Ignorar job_controller
                continue
            try:
                job = Cronjob.objects.get(app_name=app_name, job_name=job_name)
            except Cronjob.DoesNotExist:
                # Inserir o JOB na tabela de JOBS #
                job_obj = JobClass()
                if job_obj.when in WHEN_SETS:
                    expressao_cron = WHEN_SETS[job_obj.when]
                else:
                    expressao_cron = WHEN_SETS["daily"]  # Default
                job = Cronjob(
                    app_name=app_name,
                    job_name=job_name,
                    expressao_cron=expressao_cron,
                )
                job.save()
                print(f"\t\tNovo job encontrado: {job_name}: {job_obj.help}")

    def run_scheduled(self):
        """Executa os jobs que estão agendados"""
        print("\tExecutar os jobs que estão agendados...")
        for sched in JobSchedule.objects.filter(
            status=JobSchedule.STATUS_AGENDADO
        ):
            agora = timezone.localtime()
            if sched.iniciar <= agora:
                sched.run_job()

    def schedule_jobs(self):
        """Criar agenda para próxima execução"""
        print("\tCriar agenda para próxima execução...")
        for job in Cronjob.objects.exclude(
            jobschedule__status__in=[
                JobSchedule.STATUS_AGENDADO,
                JobSchedule.STATUS_EXECUTANDO,
            ]
        ):
            sched = job.next_schedule()
            print(
                f"\t\tAgendado job {sched.job.job_name} "
                f"para {localize(sched.iniciar)}"
            )

    def remove_old_logs(self):
        print("\tExcluir logs antigos...")
        for job in Cronjob.objects.exclude(manter_logs=0):
            limite = timezone.localtime() - timezone.timedelta(
                days=job.manter_logs
            )
            result = JobSchedule.objects.filter(
                job=job,
                status=JobSchedule.STATUS_CONCLUIDO,
                iniciado__lt=limite,
            ).delete()
            if result[0] > 0:
                print(f"\t\t{result[0]} logs excluídos do job '{job}'")
