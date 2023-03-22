import datetime
import docutils.core
from django.core.mail import mail_admins
from django.utils.translation import gettext as _
from sigi.apps.convenios.models import Gescon
from sigi.apps.utils.management.jobs import JobReportMixin, QuarterDailyJob


class Job(JobReportMixin, QuarterDailyJob):
    help = "Carga de dados do Gescon."

    def do_job(self):
        gescon = Gescon.load()
        gescon.importa_contratos()
        self.report_data = gescon.ultima_importacao.splitlines()
