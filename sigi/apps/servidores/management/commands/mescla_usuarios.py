from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from sigi.apps.servidores.models import Servidor
from sigi.apps.servidores.utils import mescla_users


class Command(BaseCommand):
    help = "Transfere os dados do usuário SOURCE para o usuário TARGET."

    def add_arguments(self, parser):
        parser.add_argument(
            "source_name",
            help="username do usuário que será removido",
            nargs=1,
            type=str,
        )
        parser.add_argument(
            "target_name",
            help="username do usuário que receberá os dados do que será removido",
            nargs=1,
            type=str,
        )

    def handle(self, *args, **options):
        source_name = options["source_name"][0]
        target_name = options["target_name"][0]

        try:
            user_source = User.objects.get(username__iexact=source_name)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f"Não existe o usuário {source_name}")
            )
            return
        try:
            user_target = User.objects.get(username__iexact=target_name)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f"Não existe o usuário {target_name}")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"Transferir dados de {user_source.get_full_name()} "
                f"para {user_target.get_full_name()}"
            )
        )

        resp = input("Continuar? [sim / NÃO]: ")

        if resp.lower() != "sim":
            self.stdout.write(self.style.NOTICE("Abortado!"))
            return

        mescla_users(
            user_source=user_source,
            user_target=user_target,
            verbose=True,
        )

        self.stdout.write("Concluído!")
