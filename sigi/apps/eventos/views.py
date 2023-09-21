import calendar
import csv
import locale
from functools import reduce
from rest_framework import mixins, generics
from typing import OrderedDict
from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template import Template, Context
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import (
    to_locale,
    get_language,
    ngettext,
    gettext as _,
)
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView
from django_weasyprint.utils import django_url_fetcher
from django_weasyprint.views import WeasyTemplateResponse
from weasyprint import HTML
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.convenios.models import Projeto
from sigi.apps.eventos.models import TipoEvento, Evento
from sigi.apps.eventos.forms import (
    SelecionaModeloForm,
    ConviteForm,
    CasaForm,
    FuncionarioForm,
    ParlamentarForm,
)
from sigi.apps.eventos.serializers import (
    EventoSerializer,
    EventoListSerializer,
)
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.servidores.models import Servidor


@login_required
@staff_member_required
def calendario(request):
    mes_pesquisa = int(request.GET.get("mes", timezone.localdate().month))
    ano_pesquisa = int(request.GET.get("ano", timezone.localdate().year))
    sel_categorias = request.GET.getlist(
        "categoria", [c[0] for c in TipoEvento.CATEGORIA_CHOICES]
    )
    sel_status = request.GET.getlist(
        "status", [s[0] for s in Evento.STATUS_CHOICES]
    )
    formato = request.GET.get("fmt", "cal")
    pdf = bool(request.GET.get("pdf", 0))

    meses = {}
    lang = to_locale(get_language()) + ".UTF-8"
    locale.setlocale(locale.LC_ALL, lang)

    for ano, mes in (
        Evento.objects.exclude(data_inicio=None)
        .values_list("data_inicio__year", "data_inicio__month")
        .order_by("data_inicio__year", "data_inicio__month")
        .distinct("data_inicio__year", "data_inicio__month")
    ):
        if ano in meses:
            meses[ano][mes] = calendar.month_name[mes]
        else:
            meses[ano] = {mes: calendar.month_name[mes]}

    eventos = (
        Evento.objects.exclude(data_inicio=None)
        .exclude(data_termino=None)
        .filter(
            data_inicio__year=ano_pesquisa,
            data_inicio__month=mes_pesquisa,
            status__in=sel_status,
            tipo_evento__categoria__in=sel_categorias,
        )
        .order_by("data_inicio")
    )

    context = {
        "ano_pesquisa": ano_pesquisa,
        "mes_pesquisa": mes_pesquisa,
        "formato": formato,
        "sel_categorias": sel_categorias,
        "categorias": dict(
            map(
                lambda x, y: (x[0], {"label": x[1], "color": y}),
                TipoEvento.CATEGORIA_CHOICES,
                ["red", "purple", "blue", "orange", "brown"],
            )
        ),
        "sel_status": sel_status,
        "status": dict(
            map(
                lambda x, y: (x[0], {"label": x[1], "icon": y}),
                Evento.STATUS_CHOICES,
                [
                    "assignment",
                    "hourglass_empty",
                    "access_time",
                    "thumbs_up_down",
                    "thumb_up",
                    "done_all",
                    "mood_bad",
                    "archive",
                ],
            )
        ),
        "meses": meses,
        "day_names": calendar.day_abbr,
        "eventos": eventos,
    }

    if formato == "cal" or pdf:
        semanas = [
            {"datas": s, "eventos": []}
            for s in calendar.Calendar().monthdatescalendar(
                ano_pesquisa, mes_pesquisa
            )
        ]

        for e in eventos:
            for s in semanas:
                if not (
                    (e.data_termino.date() < s["datas"][0])
                    or (e.data_inicio.date() > s["datas"][-1])
                ):
                    start = max(s["datas"][0], e.data_inicio.date())
                    end = min(s["datas"][-1], e.data_termino.date())
                    s["eventos"].append(
                        (
                            e,
                            (
                                start.weekday(),
                                end.weekday() - start.weekday() + 1,
                                6 - end.weekday(),
                            ),
                        )
                    )

        context["semanas"] = semanas

    if pdf:
        context["title"] = _("Calendário de eventos")
        context["pdf"] = True
        # return render(request, "eventos/calendario_pdf.html", context)
        return WeasyTemplateResponse(
            filename=f"calendario_{ano_pesquisa:04}{mes_pesquisa:02}.pdf",
            request=request,
            template="eventos/calendario_pdf.html",
            context=context,
            content_type="application/pdf",
        )
    else:
        return render(request, "eventos/calendario.html", context)


class EventoListView(ListView):
    model = Evento
    paginate_by = 100
    template_name = "eventos/lista.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"embed": bool(self.request.GET.get("embed", False))})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            status=Evento.STATUS_CONFIRMADO, publicar=True
        ).order_by("data_inicio")

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@login_required
@staff_member_required
def alocacao_equipe(request):
    ano_pesquisa = int(request.GET.get("ano", timezone.localdate().year))
    mes_pesquisa = int(request.GET.get("mes", 0))
    semana_pesquisa = int(request.GET.get("semana", 0))
    formato = request.GET.get("fmt", "html")

    lang = to_locale(get_language()) + ".UTF-8"
    locale.setlocale(locale.LC_ALL, lang)

    dados = []
    eventos = Evento.objects.exclude(status="C").prefetch_related("equipe_set")

    num_cols = 12

    if mes_pesquisa > 0:
        semanas = [
            [s[0], s[-1]]
            for s in calendar.Calendar().monthdatescalendar(
                ano_pesquisa, mes_pesquisa
            )
        ]
        num_cols = len(semanas)
        if semana_pesquisa > 0:
            dias = calendar.Calendar().monthdatescalendar(
                ano_pesquisa, mes_pesquisa
            )[semana_pesquisa - 1]
            num_cols = len(dias)
            eventos = eventos.filter(
                data_inicio__gte=dias[0], data_inicio__lte=dias[-1]
            )
        else:
            eventos = eventos.filter(
                data_inicio__gte=semanas[0][0],
                data_inicio__lte=semanas[-1][-1],
            )
    else:
        eventos = eventos.filter(data_inicio__year=ano_pesquisa)

    for evento in eventos:
        for p in evento.equipe_set.all():
            registro = None
            for r in dados:
                if r[0] == p.membro.pk:
                    registro = r
                    break
            if not registro:
                if semana_pesquisa > 0:
                    registro = [
                        p.membro.pk,
                        p.membro.nome_completo,
                        OrderedDict([(dia, []) for dia in dias]),
                    ]
                else:
                    registro = [
                        p.membro.pk,
                        p.membro.nome_completo,
                        [{"dias": 0, "eventos": 0} for __ in range(num_cols)],
                    ]
                dados.append(registro)

            if mes_pesquisa > 0:
                if semana_pesquisa > 0:
                    for dia in dias:
                        if (
                            evento.data_inicio.date()
                            <= dia
                            <= evento.data_termino.date()
                        ):
                            registro[2][dia].append(evento)
                else:
                    for idx, [inicio, fim] in enumerate(semanas):
                        if inicio <= evento.data_inicio.date() <= fim:
                            registro[2][idx]["dias"] += (
                                min(fim, evento.data_termino.date())
                                - evento.data_inicio.date()
                            ).days + 1
                            registro[2][idx]["eventos"] += 1
                        elif inicio <= evento.data_termino.date() <= fim:
                            registro[2][idx]["dias"] += (
                                min(fim, evento.data_termino.date())
                                - evento.data_inicio.date()
                            ).days + 1
                            registro[2][idx]["eventos"] += 1
            else:
                registro[2][evento.data_inicio.month - 1]["dias"] += (
                    evento.data_termino - evento.data_inicio
                ).days + 1
                registro[2][evento.data_inicio.month - 1]["eventos"] += 1

    dados.sort(key=lambda x: x[1])

    meses = list(calendar.month_abbr)[1:]
    linhas = []

    if semana_pesquisa:
        linhas = [
            [registro[1]] + list(registro[2].values()) for registro in dados
        ]
    else:
        for r in dados:
            r[2].append(
                reduce(
                    lambda x, y: {
                        "dias": x["dias"] + y["dias"],
                        "eventos": x["eventos"] + y["eventos"],
                    },
                    r[2],
                )
            )
            linhas.append(
                [r[1]]
                + [
                    _(
                        ngettext("%(dias)s dia", "%(dias)s dias", d["dias"])
                        + " em "
                        + ngettext(
                            "%(eventos)s evento",
                            "%(eventos)s eventos",
                            d["eventos"],
                        )
                    )
                    % d
                    if d["dias"] > 0 or d["eventos"] > 0
                    else ""
                    for d in r[2]
                ]
            )

    context = {
        "anos": Evento.objects.exclude(data_inicio=None)
        .order_by("data_inicio__year")
        .distinct("data_inicio__year")
        .values_list("data_inicio__year", flat=True),
        "ano_pesquisa": ano_pesquisa,
        "linhas": linhas,
    }

    if mes_pesquisa > 0:
        context["mes_pesquisa"] = mes_pesquisa
        context["meses"] = meses
        if semana_pesquisa > 0:
            cabecalho = [_("Servidor")] + dias
            context["semana_pesquisa"] = semana_pesquisa
            context["eventos"] = eventos
        else:
            cabecalho = (
                [_("Servidor")]
                + [
                    _(f"de {inicio:%d/%m} a {fim:%d/%m}")
                    for inicio, fim in semanas
                ]
                + ["total"]
            )
    else:
        cabecalho = [_("Servidor")] + meses + ["total"]

    context["cabecalho"] = cabecalho

    if formato == "pdf":
        context["title"] = _("Alocação de equipe")
        context["pdf"] = True
        return WeasyTemplateResponse(
            # filename="alocacao_equipe.pdf",
            request=request,
            template="eventos/alocacao_equipe_pdf.html",
            context=context,
            content_type="application/pdf",
        )
    elif formato == "csv":
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="alocacao_equipe_%s.csv"' % (ano_pesquisa,)
        writer = csv.writer(response)
        writer.writerow(cabecalho)
        writer.writerows(linhas)
        return response

    return render(request, "eventos/alocacao_equipe.html", context)


class ApiEventoAbstract:
    queryset = (
        Evento.objects.filter(publicar=True)
        .exclude(data_inicio=None)
        .exclude(data_termino=None)
        .order_by("-data_inicio")
    )
    serializer_class = EventoSerializer


class ApiEventoList(ApiEventoAbstract, generics.ListAPIView):
    """
    Lista de eventos, oficinas e cursos realizados pelo ILB / Interlegis
    """

    serializer_class = EventoListSerializer


class ApiEventoRetrieve(ApiEventoAbstract, generics.RetrieveAPIView):
    """
    Recupera um evento pelo id
    """

    pass
