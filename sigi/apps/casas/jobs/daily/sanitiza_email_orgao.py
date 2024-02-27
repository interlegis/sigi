from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.casas.models import Orgao
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils.management.jobs import JobReportMixin
from email_validator import validate_email, EmailNotValidError


class Job(JobReportMixin, DailyJob):
    help = (
        "Sanitiza sintaxe dos e-mails dos órgãos cadastrados, "
        "removendo os que não são válidos"
    )

    def do_job(self):
        self.report_data = []
        corrigidos = []
        apagados = []
        total_corrigido = 0
        total_apagado = 0
        queryset = Orgao.objects.exclude(email="")
        for orgao in queryset:
            email = orgao.email
            tentar = True
            limpar = False
            while tentar:
                try:
                    mail_info = validate_email(
                        email, check_deliverability=False
                    )
                    email = mail_info.normalized
                    tentar = False
                except EmailNotValidError as e:
                    msg = str(e)
                    if msg == "An email address cannot end with a period.":
                        email = email[:-1]
                    elif (
                        msg
                        == "An email address cannot have a period immediately after the @-sign."
                    ):
                        email = email.replace("@.", "@")
                    elif (
                        msg
                        == "An email address cannot have two periods in a row."
                    ):
                        email = email.replace("..", ".")
                    elif msg.startswith(
                        "The part after the @-sign contains invalid characters:"
                    ):
                        email = email.replace(msg[-3:-2], "")
                    else:
                        tentar = False
                        limpar = True
                        apagados.append(
                            _(
                                f"{orgao.email} do órgão {orgao.nome} "
                                f"({orgao.id}) foi excluído porque não "
                                f"pode ser corrigido: {str(e)}"
                            )
                        )
            if limpar:
                orgao.email = ""
                orgao.save()
                total_apagado += 1
            elif orgao.email != email:
                corrigidos.append(
                    _(
                        f"{orgao.email} corrigido para {email} do órgão "
                        f"{orgao.nome} ({orgao.id})"
                    )
                )
                total_corrigido += 1
                orgao.email = email
                orgao.save()

        self.report_data.extend(
            [
                _("RESUMO"),
                "------",
                "",
            ]
        )
        self.report_data.append(_(f"E-mails verificados: {queryset.count()}"))
        self.report_data.append(_(f"E-mails corrigidos.: {total_corrigido}"))
        self.report_data.append(_(f"E-mails apagados...: {total_apagado}"))
        self.report_data.extend(
            [
                "",
                _("E-MAILS CORRIGIDOS"),
                "------------------",
                "",
            ]
        )
        self.report_data.extend(corrigidos)
        self.report_data.extend(
            [
                "",
                _("E-MAILS APAGADOS"),
                "----------------",
                "",
            ]
        )
        self.report_data.extend(apagados)
