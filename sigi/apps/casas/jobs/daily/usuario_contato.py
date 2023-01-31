from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.casas.models import Funcionario
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils.mixins import JobReportMixin


class Job(JobReportMixin, DailyJob):
    help = "Ativa / desativa usuários para os Contatos Interlegis"

    def do_job(self):
        self.report_data = []
        tot_news = 0
        tot_updates = 0
        tot_deactivated = 0

        # Seleciona contatos interlegis com mínimo de informações
        # (nome, cpf, email). Elegíveis para fazer login no sistema
        contatos = Funcionario.objects.filter(
            setor="contato_interlegis"
        ).exclude(Q(nome="") | Q(cpf="") | Q(email=""))

        # Ativa / atualiza usuários para os contatos interlegis elegíveis
        for contato in contatos:
            email = contato.email
            first, *__, last = f"{contato.nome} ".split(" ")
            user, created = User.objects.update_or_create(
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                },
                username=email,
            )
            if created:
                tot_news += 1
                self.admin_log_addition(user, "Novo contato técnico habilitado")
            else:
                tot_updates += 1
                self.admin_log_change(user, "Contato técnico atualizado")

            self.report_data.append(
                _(
                    f"Usuário '{user.username}' "
                    f"{['atualizado', 'criado'][created]} "
                    f"para o contato {contato.id}"
                )
            )

        # Desativa usuários de contatos que não estão na lista de elegíveis
        for user in User.objects.filter(
            username__contains="@", is_active=True
        ).exclude(username__in=contatos.values_list("email", flat=True)):
            user.is_active = False
            user.save()
            self.admin_log_change(
                user,
                _("Desativado pelo sistema - Não é mais contato técnico"),
            )
            tot_deactivated += 1

        self.report_data.append("")
        self.report_data.append(_("RESUMO"))
        self.report_data.append("------")
        self.report_data.append("")
        self.report_data.append(_(f"{tot_news} novos usuários"))
        self.report_data.append(_(f"{tot_updates} usuários atualizados"))
        self.report_data.append(_(f"{tot_deactivated} usuários desativados"))
