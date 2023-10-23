from django_extensions.management.jobs import DailyJob
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from sigi.apps.utils.management.jobs import JobReportMixin
from sigi.apps.eventos.models import Evento

INSCRICOES_ENCERRADAS = _("INSCRIÇÕES ENCERRADAS")


class Job(JobReportMixin, DailyJob):
    help = _(
        "Encerra inscrições e despublica eventos do Portal se já ocorreram"
    )
    report_data = []

    def do_job(self):
        hoje = timezone.localtime()
        anteontem = hoje - timezone.timedelta(days=3)

        encerrar_inscricao = (
            Evento.objects.exclude(publicar=False)
            .filter(data_inicio__gte=hoje)
            .exclude(chave_inscricao=INSCRICOES_ENCERRADAS)
        )
        encerrar_inscricao.update(chave_inscricao=INSCRICOES_ENCERRADAS)

        self.report_data.append(_("Inscrições encerradas"))
        self.report_data.append("---------------------")
        self.report_data.append("")
        self.report_data.extend(
            [f"{e.nome} ({e.id})" for e in encerrar_inscricao]
        )
        self.report_data.append("")

        despublicar = Evento.objects.exclude(publicar=False).filter(
            data_termino__lte=anteontem
        )
        despublicar.update(publicar=False)

        self.report_data.append(_("Despublicados"))
        self.report_data.append("-------------")
        self.report_data.append("")
        self.report_data.extend([f"{e.nome} ({e.id})" for e in despublicar])
        self.report_data.append("")

        self.report_data.append(_("RESUMO"))
        self.report_data.append("------")
        self.report_data.append("")
        self.report_data.append(
            _(
                "* Total de eventos alterados para inscrições encerradas: "
                f"{encerrar_inscricao.count()}"
            )
        )
        self.report_data.append(
            _(
                "* Total de eventos despublicados do portal: "
                f"{despublicar.count()}"
            )
        )
        self.report_data.append("")
