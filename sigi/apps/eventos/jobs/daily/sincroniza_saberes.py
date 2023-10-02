from django_extensions.management.jobs import DailyJob
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from sigi.apps.eventos.models import Evento


class Job(DailyJob):
    help = "Sincroniza número de inscritos e aprovados com o Saberes."

    def execute(self):
        print("Sincronizando número de inscritos e aprovados com o Saberes.")
        print(f"  Início: {timezone.localtime(): %d/%m/%Y %H:%M:%S}")

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

        print(f"    total de eventos a sincronizar: {eventos.count()}")

        for e in eventos:
            try:
                e.sincroniza_saberes()
            except Evento.SaberesSyncException as err:
                print(
                    f"    Erro ao sincronizar evento {e.id}, "
                    f"com a mensagem '{err.message}'"
                )
        print(f"  Término: {timezone.localtime(): %d/%m/%Y %H:%M:%S}")
