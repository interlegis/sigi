from django.core.management.base import BaseCommand
from sigi.apps.eventos.models import Evento
from django.utils import timezone


class Command(BaseCommand):
    help = "Carrega dados de participantes de eventos do Moodle para o SIGI"

    def handle(self, *args, **options):
        for evento in Evento.objects.exclude(moodle_courseid=None).filter(
            data_termino__lt=timezone.localtime()
        ):
            try:
                evento.sincroniza_saberes()
                self.stdout.write(
                    self.style.SUCCESS(f"✔ {evento.nome} sincronizado.")
                )
            except Evento.SaberesSyncException as err:
                self.stdout.write(
                    self.style.ERROR(f"✖ {evento.nome}: {err.message}")
                )
