from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from sigi.apps.servicos.models import Servico


class Command(BaseCommand):
    help = _(
        "Atualiza a informação de data de último serviço dos serviços SEIT hospedados no Interlegis."
    )

    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        queryset = Servico.objects.exclude(url="").exclude(
            tipo_servico__string_pesquisa=""
        )
        for obj in queryset:
            obj.atualiza_data_uso()
            if ((verbosity == 1) and (obj.data_ultimo_uso is None)) or (
                verbosity > 1
            ):
                self.stdout.write(
                    f"{obj.url} \t {obj.data_ultimo_uso} \t "
                    f"{obj.erro_atualizacao}"
                )
