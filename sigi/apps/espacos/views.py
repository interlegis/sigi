import calendar
import locale
from typing import Any
from django import http
from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import (
    to_locale,
    get_language,
    ngettext,
    gettext as _,
)
from django.views.generic.base import TemplateView
from django_weasyprint.views import WeasyTemplateResponse
from sigi.apps.espacos.models import Espaco, Reserva


class Agenda(TemplateView):
    def _is_pdf(self):
        return bool(self.request.GET.get("pdf", 0))

    def get_template_names(self):
        if self._is_pdf():
            return ["espacos/agenda_pdf.html"]
        else:
            return ["espacos/agenda.html"]

    def get_context_data(self, **kwargs):
        mes_pesquisa = int(
            self.request.GET.get("mes", timezone.localdate().month)
        )
        ano_pesquisa = int(
            self.request.GET.get("ano", timezone.localdate().year)
        )
        sel_espacos = self.request.GET.getlist(
            "espaco", list(Espaco.objects.values_list("id", flat=True))
        )

        meses = {}
        lang = to_locale(get_language()) + ".UTF-8"
        locale.setlocale(locale.LC_ALL, lang)

        for ano, mes in (
            Reserva.objects.values_list("inicio__year", "inicio__month")
            .order_by("inicio__year", "inicio__month")
            .distinct("inicio__year", "inicio__month")
        ):
            if ano in meses:
                meses[ano][mes] = calendar.month_name[mes]
            else:
                meses[ano] = {mes: calendar.month_name[mes]}

        espacos = list(Espaco.objects.all())

        semanas = [
            {"datas": s, "reservas": {espaco: [] for espaco in espacos}}
            for s in calendar.Calendar().monthdatescalendar(
                ano_pesquisa, mes_pesquisa
            )
        ]

        primeiro_dia = timezone.make_aware(
            timezone.datetime(*semanas[0]["datas"][0].timetuple()[:6])
        )
        ultimo_dia = timezone.make_aware(
            timezone.datetime(*semanas[-1]["datas"][-1].timetuple()[:6])
        )

        for reserva in Reserva.objects.exclude(
            status=Reserva.STATUS_CANCELADO
        ).filter(
            Q(inicio__range=[primeiro_dia, ultimo_dia])
            | Q(termino__range=[primeiro_dia, ultimo_dia])
        ):
            for semana in semanas:
                if not (
                    (reserva.termino.date() < semana["datas"][0])
                    or (reserva.inicio.date() > semana["datas"][-1])
                ):
                    start = max(semana["datas"][0], reserva.inicio.date())
                    end = min(semana["datas"][-1], reserva.termino.date())
                    semana["reservas"][reserva.espaco].append(
                        [
                            reserva,
                            [
                                start.weekday(),
                                end.weekday() - start.weekday() + 1,
                                6 - end.weekday(),
                            ],
                        ]
                    )

        for semana in semanas:
            for espaco, reservas in semana["reservas"].items():
                last_pos = 0
                for reserva in reservas:
                    if last_pos > 0:
                        reserva[1][0] -= last_pos
                    last_pos += reserva[1][0] + reserva[1][1]

        context = super().get_context_data(**kwargs)
        context["mes_pesquisa"] = mes_pesquisa
        context["ano_pesquisa"] = ano_pesquisa
        context["sel_espacos"] = sel_espacos
        context["meses"] = meses
        context["espacos"] = Espaco.objects.all()
        context["semanas"] = semanas
        context["day_names"] = calendar.day_abbr

        if self._is_pdf():
            context["pdf"] = True
            context["title"] = _("Reserva de espaços do ILB")

        return context

    def render_to_response(self, context, **response_kwargs):
        self.response_class = TemplateResponse
        self.content_type = None
        if self._is_pdf():
            self.content_type = "application/pdf"
            self.response_class = WeasyTemplateResponse
            response_kwargs.setdefault(
                "filename", f"agenda-{timezone.localdate()}.pdf"
            )
        return super().render_to_response(context, **response_kwargs)
