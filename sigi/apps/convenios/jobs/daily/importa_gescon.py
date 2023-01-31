import datetime
import docutils.core
from django.core.mail import mail_admins
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.convenios.models import Gescon
from sigi.apps.utils.mixins import JobReportMixin


class Job(JobReportMixin, DailyJob):
    help = "Carga de dados do Gescon."

    def do_job(self):
        gescon = Gescon.load()
        gescon.importa_contratos()
        self.report_data = gescon.ultima_importacao.splitlines()
