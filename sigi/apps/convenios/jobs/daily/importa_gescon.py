import datetime
import docutils.core
from django.core.mail import mail_admins
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.convenios.models import Gescon


class Job(DailyJob):
    help = "Carga de dados do Gescon."

    def execute(self):
        now = datetime.datetime.now()
        print(f"Import gescon data started at {now:%Y-%m-%d %H:%M:%S}")
        gescon = Gescon.load()
        gescon.importa_contratos()
        self.report(gescon, now)
        now = datetime.datetime.now()
        print(f"Import gescon data finished at {now:%Y-%m-%d %H:%M:%S}")

    def report(self, gescon, now):
        rst = gescon.ultima_importacao
        html = docutils.core.publish_string(
            rst,
            writer_name="html5",
            settings_overrides={
                "input_encoding": "unicode",
                "output_encoding": "unicode",
            },
        )
        mail_admins(
            subject=_(f"Importação do GESCON em {now:%d/%m/%Y às %Hh%M}"),
            message=rst,
            html_message=html,
            fail_silently=True,
        )
