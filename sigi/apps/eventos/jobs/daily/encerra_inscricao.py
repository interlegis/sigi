from django_extensions.management.jobs import DailyJob
from django.utils import timezone
from django.utils.translation import gettext as _
from sigi.apps.utils.models import Config
from sigi.apps.eventos.models import Evento

INSCRICOES_ENCERRADAS = _("INSCRIÇÕES ENCERRADAS")


class Job(DailyJob):
    help = _(
        "Encerra inscrições e despublica eventos do Portal se já ocorreram"
    )
    report_data = []

    def execute(self):
        dias_a_retroagir = int(Config.get_param("ENCERRA_INSCRICAO")[0])
        self.report_data = []
        hoje = timezone.localtime().replace(hour=23, minute=59, second=59)
        retroagir = hoje - timezone.timedelta(days=dias_a_retroagir)
        total_encerrar = 0
        total_despublicar = 0

        encerrar_inscricao = (
            Evento.objects.exclude(publicar=False)
            .filter(data_inicio__lte=hoje)
            .exclude(chave_inscricao=INSCRICOES_ENCERRADAS)
        )

        if encerrar_inscricao.exists():
            print(_("Inscrições encerradas"))
            print("---------------------")
            print("")
            print("\n".join([f"{e.nome} ({e.id})" for e in encerrar_inscricao]))
            print("")

            total_encerrar = encerrar_inscricao.update(
                chave_inscricao=INSCRICOES_ENCERRADAS
            )

        despublicar = Evento.objects.exclude(publicar=False).filter(
            data_termino__lte=retroagir
        )

        if despublicar.exists():
            print("")
            print(_("Despublicados"))
            print("-------------")
            print("")
            print("\n".join([f"{e.nome} ({e.id})" for e in despublicar]))
            print("")

            total_despublicar = despublicar.update(publicar=False)

        if total_encerrar > 0 or total_despublicar > 0:
            print("")
            print(_("RESUMO"))
            print("------")
            print("")
            if total_encerrar > 0:
                print(
                    _(
                        "* Total de eventos alterados para inscrições "
                        "encerradas: {count}"
                    ).format(count=total_encerrar)
                )
            if total_despublicar > 0:
                print(
                    _(
                        "* Total de eventos despublicados do portal: {count}"
                    ).format(count=total_despublicar)
                )
