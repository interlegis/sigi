from django.core.management.base import BaseCommand
from sigi.apps.servidores.models import Servidor
from sigi.apps.servidores.utils import mescla_servidores


class Command(BaseCommand):
    help = "Transfere os dados do servidor SOURCE para o servidor TARGET."

    def add_arguments(self, parser):
        parser.add_argument(
            "source_id",
            help="ID do servidor que será removido",
            nargs=1,
            type=int,
        )
        parser.add_argument(
            "target_id",
            help="ID do servidor que receberá os dados do que será removido",
            nargs=1,
            type=int,
        )

    def handle(self, *args, **options):
        source_id = options["source_id"][0]
        target_id = options["target_id"][0]

        try:
            servidor_source = Servidor.objects.get(id=source_id)
        except Servidor.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f"Não existe servidor com ID {source_id}")
            )
            return
        try:
            servidor_target = Servidor.objects.get(id=target_id)
        except Servidor.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f"Não existe servidor com ID {target_id}")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"Transferir dados de {servidor_source.nome_completo} "
                f"para {servidor_target.nome_completo}"
            )
        )

        resp = input("Continuar? [sim / NÃO]: ")

        if resp.lower() != "sim":
            self.stdout.write(self.style.NOTICE("Abortado!"))
            return

        mescla_servidores(
            servidor_source=servidor_source,
            servidor_target=servidor_target,
            verbose=True,
        )

        self.stdout.write("Concluído!")
