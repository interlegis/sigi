import ldap
from django.conf import settings
from django.utils.translation import gettext as _
from django_auth_ldap.config import _DeepStringCoder
from django_extensions.management.jobs import DailyJob
from sigi.apps.utils.management.jobs import JobReportMixin
from sigi.apps.servidores.models import Servico, Servidor
from sigi.apps.servidores.utils import (
    servidor_update_from_ldap,
    servidor_create_or_update,
    user_staff_and_group,
)


class Job(JobReportMixin, DailyJob):
    help = _("Sincroniza servidores com o ldap")
    report_data = []

    def do_job(self):
        coder = _DeepStringCoder("utf8")

        connect = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        connect.protocol_version = 3
        connect.set_option(ldap.OPT_REFERRALS, 0)
        connect.simple_bind_s(
            settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD
        )
        page_control = ldap.controls.SimplePagedResultsControl(
            True, size=1000, cookie=""
        )

        total_ldap = 0
        total_create = 0
        total_update = 0
        total_deactive = 0

        servidores = {
            s.ldap_dn: s
            for s in Servidor.objects.exclude(ldap_dn="").exclude(externo=True)
        }

        while True:
            response = connect.search_ext(
                settings.AUTH_LDAP_USER,
                ldap.SCOPE_ONELEVEL,
                settings.LDAP_GET_ALL_USERS,
                serverctrls=[page_control],
            )
            rtype, rdata, rmsgid, serverctrls = connect.result3(response)
            decoded_data = coder.decode(rdata)

            controls = [
                control
                for control in serverctrls
                if control.controlType
                == ldap.controls.SimplePagedResultsControl.controlType
            ]
            if not controls:
                raise Exception("The LDAP server ignores RFC 2696 control")

            for dn, ldap_user in decoded_data:
                total_ldap += 1
                resp, servidor = servidor_create_or_update(
                    ldap_attrs=ldap_user
                )
                if servidor.user:
                    user_staff_and_group(servidor.user, ldap_user)
                if resp == servidor_create_or_update.UPDATED:
                    total_update += 1
                    self.report_data.append(
                        _(f"{servidor.nome_completo} atualizado")
                    )
                elif resp == servidor_create_or_update.CREATED:
                    total_create += 1
                    self.report_data.append(
                        _(f"{servidor.nome_completo} criado")
                    )

                if dn in servidores:
                    del servidores[dn]

            if not controls[0].cookie:
                break
            page_control.cookie = controls[0].cookie

        for dn, servidor in servidores.items():
            rdata = connect.search_s(
                settings.AUTH_LDAP_USER,
                ldap.SCOPE_SUBTREE,
                ldap.filter.filter_format("(distinguishedName=%s)", [dn]),
            )

            if rdata:
                ldap_attrs = coder.decode(rdata[0][1])
                if servidor.user:
                    user_staff_and_group(servidor.user, ldap_attrs)
                if (
                    servidor_update_from_ldap(servidor, ldap_attrs)
                    == servidor_create_or_update.UPDATED
                ):
                    total_update += 1
            else:
                if servidor.user:
                    servidor.user.is_active = False
                    total_deactive += 1

        # Reporta servidores que não estão no LDAP e também não são externos

        self.report_data.append("")
        self.report_data.append(
            _(
                "Servidores que não estão no LDAP e também não estão marcados "
                "como Externos"
            )
        )
        self.report_data.append("=" * 72)
        self.report_data.append("")

        for s in Servidor.objects.filter(
            ldap_dn="", externo=False, sigi=False
        ).order_by("nome_completo"):
            self.report_data.append(f"- {s.nome_completo}")

        self.report_data.append("")
        self.report_data.append("RESUMO")
        self.report_data.append("=" * 6)
        self.report_data.append("")
        self.report_data.append(f"* {total_ldap} usuários lidos do LDAP")
        self.report_data.append(f"* {total_create} novos servidores criados")
        self.report_data.append(f"* {total_update} servidores atualizados")
        self.report_data.append(f"* {total_deactive} usuários desativados")
        self.report_data.append("")
