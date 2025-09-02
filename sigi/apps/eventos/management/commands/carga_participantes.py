from django.core.management.base import BaseCommand
from django.utils import timezone
from sigi.apps.eventos.models import Evento
from sigi.apps.eventos.saberes import SaberesSyncException


class Command(BaseCommand):
    help = "Carrega dados de participantes de eventos do Moodle para o SIGI"

    def handle(self, *args, **options):
        eventos = Evento.objects.exclude(moodle_courseid=None).filter(
            data_termino__lt=timezone.localtime()
        )
        self.stdout.write(f"Processando {eventos.count()} eventos:")
        counter = 0
        for evento in eventos:
            counter += 1
            try:
                evento.sincroniza_saberes()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✔ {counter}: {evento.nome} sincronizado."
                    )
                )
            except SaberesSyncException as err:
                self.stdout.write(
                    self.style.ERROR(
                        f"✖ {counter}: {evento.nome}: {err.message}"
                    )
                )
