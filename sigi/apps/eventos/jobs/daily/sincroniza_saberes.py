import sys
from django_extensions.management.jobs import DailyJob
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.translation import gettext as _
from sigi.apps.eventos.models import Evento
from sigi.apps.eventos.saberes import SaberesSyncException


class Job(DailyJob):
    help = _("Sincroniza número de inscritos e aprovados com o Saberes.")

    def execute(self):
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
                    print(
                        _("Evento {nome} ({id}) atualizado").format(
                            nome=evento.nome, id=evento.id
                        )
                    )
                    total_sinc += 1
                else:
                    total_ok += 1
            except SaberesSyncException as err:
                print(
                    _(
                        "Erro ao sincronizar evento {nome} ({id}), "
                        "com a mensagem '{message}'"
                    ).format(
                        nome=evento.nome, id=evento.id, message=err.message
                    ),
                    file=sys.stderr,
                )
                total_erros += 1

        if eventos.count() > 0:
            print(_("RESUMO"))
            print("------")
            print("")
            print(
                _("* Eventos a sincronizar: {count}").format(
                    count=eventos.count()
                )
            )
            print(_("* Eventos atualizados: {count}").format(count=total_sinc))
            print(_("* Já estavam corretos: {count}").format(count=total_ok))
            print(_("* Erros: {count}").format(count=total_erros))
            print("")
