import sys
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.casas.models import Orgao
from email_validator import validate_email, EmailNotValidError


class Job(DailyJob):
    help = (
        "Sanitiza sintaxe dos e-mails dos órgãos cadastrados, "
        "removendo os que não são válidos"
    )

    def execute(self):
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
            if limpar:
                apagados.append(
                    _(
                        "{email} do órgão {nome} ({id}) foi excluído porque "
                        "não pode ser corrigido: {msg}"
                    ).format(
                        email=orgao.email,
                        nome=orgao.nome,
                        id=orgao.id,
                        msg=msg,
                    )
                )
                orgao.email = ""
                orgao.save()
                total_apagado += 1
            elif orgao.email != email:
                corrigidos.append(
                    _(
                        "{email} corrigido para {novo_email} do órgão "
                        "{nome} ({id})"
                    ).format(
                        email=orgao.email,
                        novo_email=email,
                        nome=orgao.nome,
                        id=orgao.id,
                    )
                )
                total_corrigido += 1
                orgao.email = email
                orgao.save()

        print(_("RESUMO"), "\n------\n\n")
        print(_("E-mails verificados: {count}").format(count=queryset.count()))
        print(_("E-mails corrigidos.: {count}").format(count=total_corrigido))
        print(_("E-mails apagados...: {count}").format(count=total_apagado))

        if total_corrigido > 0:
            print("\n\n", _("E-MAILS CORRIGIDOS"), "\n------------------\n\n")
            print("\n".join(corrigidos))

        if total_apagado > 0:
            print(
                "\n\n",
                _("E-MAILS APAGADOS"),
                "\n----------------\n\n",
                file=sys.stderr,
            )
            print("\n".join(apagados), file=sys.stderr)
