import dns.resolver
from django.utils import timezone
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.servicos.models import Servico
from sigi.apps.utils.mixins import JobReportMixin


class Job(JobReportMixin, DailyJob):
    help = "Verifica domínios registrados no Interlegis"
    report_data = []

    def do_job(self):
        servicos = Servico.objects.filter(
            tipo_servico__modo="R", data_desativacao=None
        ).exclude(url="")
        total = servicos.count()
        erros = 0
        for s in servicos:
            s.data_verificacao = timezone.localtime()
            try:
                dns.resolver.resolve(s.url, "SOA")
                s.resultado_verificacao = "F"
                s.erro_atualizacao = ""
            except Exception as e:
                erros += 1
                s.resultado_verificacao = "O"
                s.erro_atualizacao = str(e)
                self.report_data.append(
                    f"  * {s.url} {s.get_resultado_verificacao_display()}: "
                    f"{s.erro_atualizacao}"
                )
            s.save()

        self.report_data = [
            "",
            "RESUMO",
            "======",
            "",
            f"  * Total de registros verificados: {total}",
            f"  * Registros com erros: {erros}",
            "",
            "",
        ] + self.report_data
