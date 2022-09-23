from django_extensions.management.jobs import DailyJob
from sigi.apps.convenios.models import Gescon
import datetime


class Job(DailyJob):
    help = "Carga de dados do Gescon."

    def execute(self):
        now = datetime.datetime.now()
        print(f"Import gescon data started at {now:%Y-%m-%d %H:%M:%S}")
        gescon = Gescon.load()
        gescon.importa_contratos()
        now = datetime.datetime.now()
        print(f"Import gescon data finished at {now:%Y-%m-%d %H:%M:%S}")
