from django_extensions.management.jobs import DailyJob
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from sigi.apps.utils.management.jobs import JobReportMixin
from sigi.apps.utils.models import Config
from sigi.apps.eventos.models import Evento

INSCRICOES_ENCERRADAS = _("INSCRIÇÕES ENCERRADAS")


class Job(JobReportMixin, DailyJob):
    help = _(
        "Encerra inscrições e despublica eventos do Portal se já ocorreram"
    )
    report_data = []

    def do_job(self):
        dias_a_retroagir = int(Config.get_param("ENCERRA_INSCRICAO")[0])
        self.report_data = []
        hoje = timezone.localtime().replace(hour=23, minute=59, second=59)
        retroagir = hoje - timezone.timedelta(days=dias_a_retroagir)

        encerrar_inscricao = (
            Evento.objects.exclude(publicar=False)
            .filter(data_inicio__lte=hoje)
            .exclude(chave_inscricao=INSCRICOES_ENCERRADAS)
        )

        self.report_data.extend(
            [
                "",
                "",
                _("Inscrições encerradas"),
                "---------------------",
                "",
            ]
        )
        self.report_data.extend(
            [f"{e.nome} ({e.id})" for e in encerrar_inscricao]
        )

        total_encerrar = encerrar_inscricao.update(
            chave_inscricao=INSCRICOES_ENCERRADAS
        )

        despublicar = Evento.objects.exclude(publicar=False).filter(
            data_termino__lte=retroagir
        )

        self.report_data.extend(
            [
                "",
                "",
                _("Despublicados"),
                "-------------",
                "",
            ]
        )
        self.report_data.extend([f"{e.nome} ({e.id})" for e in despublicar])

        total_despublicar = despublicar.update(publicar=False)

        self.report_data.extend(
            [
                "",
                "",
                _("RESUMO"),
                "------",
                "",
                _(
                    "* Total de eventos alterados para inscrições encerradas: "
                    f"{total_encerrar}"
                ),
                _(
                    "* Total de eventos despublicados do portal: "
                    f"{total_despublicar}"
                ),
            ]
        )
