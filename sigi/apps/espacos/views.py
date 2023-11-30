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
                sel_espacos.filter(q_virtual, reserva__status=Reserva.STATUS_ATIVO)
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
