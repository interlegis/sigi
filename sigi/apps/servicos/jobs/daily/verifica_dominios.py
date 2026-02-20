import sys
import dns.resolver
from django.utils import timezone
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.servicos.models import Servico


class Job(DailyJob):
    help = "Verifica domínios registrados no Interlegis"

    def execute(self):
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
                print(
                    f"  * {s.url} {s.get_resultado_verificacao_display()}: "
                    f"{s.erro_atualizacao}",
                    file=sys.stderr,
                )
            s.save()

            print(f"  * Total de registros verificados: {total}")
            print(f"  * Registros com erros: {erros}")
