from django_extensions.management.jobs import DailyJob
from django.db.models import Q
from django.conf import settings
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.translation import gettext as _
from sigi.apps.utils.management.jobs import JobReportMixin
from sigi.apps.eventos.models import Evento
from sigi.apps.eventos.saberes import SaberesSyncException


class Job(JobReportMixin, DailyJob):
    help = _("Sincroniza número de inscritos e aprovados com o Saberes.")
    report_data = []

    def do_job(self):
        self.report_data = []
        infos = []
        errors = []
        total_sinc = 0
        total_ok = 0
        total_erros = 0
        trintadias = timezone.localtime() - timezone.timedelta(days=30)
        eventos = Evento.objects.exclude(moodle_courseid=None).filter(
            (
                Q(data_sincronizacao=None)
                & Q(data_termino__lte=timezone.localtime())
            )
            | (
                Q(data_termino__gte=trintadias)
                & Q(data_termino__lte=timezone.localtime())
            )
        )

        for evento in eventos:
            initial = model_to_dict(evento)
            try:
                evento.sincroniza_saberes()
                if model_to_dict(evento) != initial:
                    infos.append(
                        f"Evento {evento.nome} ({evento.id}) atualizado"
                    )
                    total_sinc += 1
                else:
                    total_ok += 1
            except SaberesSyncException as err:
                errors.append(
                    _(
                        f"Erro ao sincronizar evento {evento.nome} "
                        f"({evento.id}), com a mensagem '{err.message}'"
                    )
                )
                total_erros += 1

        self.report_data.append(_("ATUALIZAÇÕES"))
        self.report_data.append("------------")
        self.report_data.append("")
        self.report_data.extend(infos)
        self.report_data.append("")

        self.report_data.append(_("ERROS"))
        self.report_data.append("-----")
        self.report_data.append("")
        self.report_data.extend(errors)
        self.report_data.append("")

        self.report_data.append(_("RESUMO"))
        self.report_data.append("------")
        self.report_data.append("")

        self.report_data.append(f"* Eventos a sincronizar: {eventos.count()}")
        self.report_data.append(f"* Eventos atualizados: {total_sinc}")
        self.report_data.append(f"* Já estavam corretos: {total_ok}")
        self.report_data.append(f"* Erros: {total_erros}")
        self.report_data.append("")
