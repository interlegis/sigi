import datetime
from django_extensions.management.jobs import DailyJob
from sigi.apps.servicos.models import Servico


class Job(DailyJob):
    help = "Atualiza uso dos serviços"

    def execute(self):
        print(
            "Atualizando uso dos serviços SEIT."
            f" Início: {datetime.datetime.now(): %d/%m/%Y %H:%M:%S}",
            end=" ",
        )
        queryset = Servico.objects.exclude(url="").exclude(
            tipo_servico__string_pesquisa=""
        )
        for obj in queryset:
            obj.atualiza_data_uso()
        print(f"Término: {datetime.datetime.now(): %d/%m/%Y %H:%M:%S}")
