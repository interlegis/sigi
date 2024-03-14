import calendar
import locale
from typing import Any
from django import http
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.utils.translation import (
    to_locale,
    get_language,
    gettext as _,
)
from django.views.generic.base import TemplateView
from sigi.apps.espacos.models import Espaco, Reserva
from sigi.apps.espacos.forms import UsoEspacoReportForm
from sigi.apps.utils.mixins import ReportViewMixin, StaffMemberRequiredMixin


class Agenda(ReportViewMixin, StaffMemberRequiredMixin, TemplateView):
    html_template_name = "espacos/agenda.html"
    pdf_template_name = "espacos/agenda_pdf.html"
    report_title = _("Reserva de espaços do ILB")
    pagesize = "A4 landscape"

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
            Reserva.objects.values_list(
                "data_inicio__year", "data_inicio__month"
            )
            .order_by("data_inicio__year", "data_inicio__month")
            .distinct("data_inicio__year", "data_inicio__month")
        ):
            if ano in meses:
                meses[ano][mes] = calendar.month_name[mes]
            else:
                meses[ano] = {mes: calendar.month_name[mes]}

        espacos = list(Espaco.objects.all())

        semanas = [
            {"datas": s}
            for s in calendar.Calendar().monthdatescalendar(
                ano_pesquisa, mes_pesquisa
            )
        ]

        primeiro_dia = semanas[0]["datas"][0]
        ultimo_dia = semanas[-1]["datas"][-1]
        shift = primeiro_dia.isocalendar().week

        for reserva in Reserva.objects.filter(
            status=Reserva.STATUS_ATIVO
        ).filter(
            Q(data_inicio__range=[primeiro_dia, ultimo_dia])
            | Q(data_termino__range=[primeiro_dia, ultimo_dia])
        ):
            for ix in range(
                reserva.data_inicio.isocalendar().week - shift,
                reserva.data_termino.isocalendar().week - shift + 1,
            ):
                if ix < 0 or ix > len(semanas):
                    continue
                semana = semanas[ix]
                start = max(semana["datas"][0], reserva.data_inicio).weekday()
                end = min(semana["datas"][-1], reserva.data_termino).weekday()
                if reserva.espaco not in semana:
                    semana[reserva.espaco] = []
                semana[reserva.espaco].append(
                    {
                        "reserva": reserva,
                        "col_start": start,
                        "col_end": end,
                    }
                )

        for semana in semanas:
            for espaco, reservas in semana.items():
                if not isinstance(espaco, Espaco):
                    continue
                horas = sorted(
                    {
                        h
                        for hh in [
                            (
                                r["reserva"].hora_inicio,
                                r["reserva"].hora_termino,
                            )
                            for r in reservas
                        ]
                        for h in hh
                    }
                )
                semana[espaco] = [
                    {"hora": h, "colunas": [False] * 7} for h in horas
                ]
                for reserva in reservas:
                    row_start = horas.index(reserva["reserva"].hora_inicio)
                    row_end = horas.index(reserva["reserva"].hora_termino)
                    col_start = reserva["col_start"]
                    col_end = reserva["col_end"]
                    semana[espaco][row_start]["colunas"][col_start] = {
                        "reserva": reserva["reserva"],
                        "colspan": col_end - col_start + 1,
                        "rowspan": row_end - row_start + 1,
                    }
                    for rx in range(row_start, row_end + 1):
                        for cx in range(col_start, col_end + 1):
                            if rx != row_start or cx != col_start:
                                semana[espaco][rx]["colunas"][cx] = None

        context = super().get_context_data(**kwargs)
        context["mes_pesquisa"] = mes_pesquisa
        context["ano_pesquisa"] = ano_pesquisa
        context["sel_espacos"] = sel_espacos
        context["meses"] = meses
        context["espacos"] = Espaco.objects.all()
        context["semanas"] = semanas
        context["day_names"] = calendar.day_abbr

        return context


class UsoEspacos(ReportViewMixin, StaffMemberRequiredMixin, TemplateView):
    html_template_name = "espacos/uso_espaco.html"
    pdf_template_name = "espacos/uso_espaco_pdf.html"
    report_title = _("Uso dos espaços - Auditórios e Salas")
    pagesize = "A4 landscape"
    attachment = False

    def get_context_data(self, **kwargs):
        form = UsoEspacoReportForm(self.request.GET)
        if form.is_valid():
            data_inicio = form.cleaned_data["data_inicio"]
            data_fim = form.cleaned_data["data_fim"]
            sel_espacos = form.cleaned_data["espaco"]
            virtual = form.cleaned_data["virtual"]
            agrupar_espacos = form.cleaned_data["agrupar_espacos"]
        else:
            form = UsoEspacoReportForm(
                initial={"espaco": Espaco.objects.all()}
            )
            semana = form.get_semana()
            data_inicio = semana["first"]
            data_fim = semana["last"]
            virtual = UsoEspacoReportForm.VIRTUAL_ALL
            agrupar_espacos = False
            sel_espacos = None

        if not sel_espacos:
            sel_espacos = Espaco.objects.all()

        if virtual == UsoEspacoReportForm.VIRTUAL_VIRTUAL:
            q_virtual = Q(virtual=True)
        elif virtual == UsoEspacoReportForm.VIRTUAL_PRESENCIAL:
            q_virtual = Q(virtual=False)
        else:
            q_virtual = Q()

        reservas_qs = (
            Reserva.objects.filter(q_virtual, status=Reserva.STATUS_ATIVO)
            .filter(
                Q(inicio__range=(data_inicio, data_fim))
                | Q(termino__range=(data_inicio, data_fim))
            )
            .order_by("inicio", "termino")
        )

        if agrupar_espacos:
            espacos = (
                sel_espacos.filter(
                    q_virtual, reserva__status=Reserva.STATUS_ATIVO
                )
                .filter(
                    Q(reserva__inicio__range=(data_inicio, data_fim))
                    | Q(reserva__termino__range=(data_inicio, data_fim))
                )
                .distinct()
                .prefetch_related(
                    Prefetch(
                        "reserva_set",
                        queryset=reservas_qs,
                        to_attr="reservas",
                    )
                )
            )
        else:
            espacos = None

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "espacos": espacos,
                "reservas": reservas_qs,
                "form": form,
                "data_inicio": data_inicio,
                "data_termino": data_fim,
                "sel_espacos": sel_espacos,
            }
        )

        return context
