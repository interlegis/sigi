from django.db.models import Q
from django.contrib.auth.models import User
from django_extensions.management.jobs import DailyJob
from sigi.apps.casas.models import Orgao, Funcionario


class Job(DailyJob):
    help = "Ativa / desativa usuários para os Contatos Interlegis"

    def execute(self):
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
            print(
                f"{['Updated', 'Created'][created]} user {user.username} for contato {contato.id}"
            )
        # Desativa usuários de contatos que não estão na lista de elegíveis
        qtd_desativados = (
            User.objects.filter(username__contains="@", is_active=True)
            .exclude(username__in=contatos.values_list("email", flat=True))
            .update(is_active=False)
        )
        print(f"{qtd_desativados} usuários desativados")
