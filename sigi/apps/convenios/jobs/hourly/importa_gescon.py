import sys
from django.utils.translation import gettext as _
from django_extensions.management.jobs import HourlyJob
from sigi.apps.convenios.models import Gescon


class Job(HourlyJob):
    help = "Carga de dados do Gescon."

    def execute(self):
        gescon = Gescon.load()
        errors = gescon.importa_contratos()
        if errors:
            print(gescon.ultima_importacao, file=sys.stderr)
        else:
            print(gescon.ultima_importacao)
