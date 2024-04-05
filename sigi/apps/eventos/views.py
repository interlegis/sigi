import calendar
import csv
import datetime
import locale
import pandas as pd
from functools import reduce
from itertools import groupby
from rest_framework import mixins, generics
from typing import OrderedDict
from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
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
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.convenios.models import Projeto
from sigi.apps.eventos.models import TipoEvento, Evento
from sigi.apps.eventos.forms import (
    SelecionaModeloForm,
    ConviteForm,
    EventosPorUfForm,
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
                    "access_time",
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
                    (e.data_termino < s["datas"][0])
                    or (e.data_inicio > s["datas"][-1])
                ):
                    start = max(s["datas"][0], e.data_inicio)
                    end = min(s["datas"][-1], e.data_termino)
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
            status=Evento.STATUS_AUTORIZADO, publicar=True
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
                        if evento.data_inicio <= dia <= evento.data_termino:
                            registro[2][dia].append(evento)
                else:
                    for idx, [inicio, fim] in enumerate(semanas):
                        if inicio <= evento.data_inicio <= fim:
                            registro[2][idx]["dias"] += (
                                min(fim, evento.data_termino)
                                - evento.data_inicio
                            ).days + 1
                            registro[2][idx]["eventos"] += 1
                        elif inicio <= evento.data_termino <= fim:
                            registro[2][idx]["dias"] += (
                                min(fim, evento.data_termino)
                                - evento.data_inicio
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
                    (
                        _(
                            ngettext(
                                "%(dias)s dia", "%(dias)s dias", d["dias"]
                            )
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
                    )
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
            filename="alocacao_equipe.pdf",
            request=request,
            template="eventos/alocacao_equipe_pdf.html",
            context=context,
            content_type="application/pdf",
        )
    elif formato == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="alocacao_equipe_%s.csv"' % (ano_pesquisa,)
        )
        writer = csv.writer(response)
        writer.writerow(cabecalho)
        writer.writerows(linhas)
        return response

    return render(request, "eventos/alocacao_equipe.html", context)


@login_required
@staff_member_required
def eventos_por_uf(request):
    formato = request.GET.get("fmt", "html")
    initials = {
        "data_inicio": datetime.date.today().replace(day=1),
        "data_fim": datetime.date.today().replace(
            day=calendar.monthrange(
                datetime.date.today().year, datetime.date.today().month
            )[1]
        ),
        "categoria": [c[0] for c in TipoEvento.CATEGORIA_CHOICES],
        "virtual": [m[0] for m in EventosPorUfForm.MODO_CHOICES],
    }
    if "data_inicio" in request.GET or "data_fim" in request.GET:
        form = EventosPorUfForm(request.GET)
    else:
        form = EventosPorUfForm(initial=initials)
    if not form.is_valid():
        return render(
            request, "eventos/eventos_por_uf.html", context={"form": form}
        )
    data_inicio = form.cleaned_data.get("data_inicio")
    data_fim = form.cleaned_data.get("data_fim")
    categorias = form.cleaned_data.get("categoria", initials["categoria"])
    virtual = form.cleaned_data.get("virtual", initials["virtual"])
    annotates = dict()
    aggfuncs = dict()
    if "P" in virtual:
        annotates["eventos_presenciais"] = Count(
            "municipio__orgao__evento__id",
            distinct=True,
            filter=Q(municipio__orgao__evento__virtual=False),
        )
        annotates["participantes_presenciais"] = Sum(
            "municipio__orgao__evento__total_participantes",
            filter=Q(municipio__orgao__evento__virtual=False),
        )
        aggfuncs["nº eventos presenciais"] = sum
        aggfuncs["participantes presenciais"] = sum
    if "V" in virtual:
        annotates["eventos_virtuais"] = Count(
            "municipio__orgao__evento__id",
            distinct=True,
            filter=Q(municipio__orgao__evento__virtual=True),
        )
        annotates["participantes_virtuais"] = Sum(
            "municipio__orgao__evento__total_participantes",
            filter=Q(municipio__orgao__evento__virtual=True),
        )
        aggfuncs["nº eventos virtuais"] = sum
        aggfuncs["participantes virtuais"] = sum
    eventos = (
        UnidadeFederativa.objects.filter(
            municipio__orgao__evento__status=Evento.STATUS_REALIZADO,
            municipio__orgao__evento__data_inicio__range=(
                data_inicio,
                data_fim,
            ),
            municipio__orgao__evento__tipo_evento__categoria__in=categorias,
        )
        .order_by("regiao", "nome")
        .values(
            "regiao",
            "nome",
            "municipio__orgao__evento__tipo_evento__categoria",
        )
        .annotate(**annotates)
    )
    df = pd.DataFrame(eventos)
    if df.empty:
        messages.add_message(
            request,
            messages.ERROR,
            _("Nenhum evento foi realizado no período solicitado"),
        )
        return render(
            request, "eventos/eventos_por_uf.html", context={"form": form}
        )
    # Renomeia colunas
    df.rename(
        columns={
            "municipio__orgao__evento__tipo_evento__categoria": "categoria",
            "eventos_presenciais": "nº eventos presenciais",
            "eventos_virtuais": "nº eventos virtuais",
            "participantes_presenciais": "participantes presenciais",
            "participantes_virtuais": "participantes virtuais",
        },
        inplace=True,
    )
    # Troca a sigla pelo nome da região
    for sigla, nome in UnidadeFederativa.REGIAO_CHOICES:
        df["regiao"].replace(sigla, nome, inplace=True)
    # Troca o código pelo nome da categoria de eventos
    for cod, nome in TipoEvento.CATEGORIA_CHOICES:
        df["categoria"].replace(cod, nome, inplace=True)
    # Cria tabela pivot das UFs
    pivo_uf = df.pivot_table(
        index=["regiao", "nome"],
        columns="categoria",
        aggfunc=aggfuncs,
        fill_value=0,
    )
    if len(categorias) > 1:
        # calcula os totais de eventos e de participantes para as UFs
        ix_eventos_presenciais = [
            i for i in pivo_uf.columns if i[0] == "nº eventos presenciais"
        ]
        ix_eventos_virtuais = [
            i for i in pivo_uf.columns if i[0] == "nº eventos virtuais"
        ]
        ix_participantes_presenciais = [
            i for i in pivo_uf.columns if i[0] == "participantes presenciais"
        ]
        ix_participantes_virtuais = [
            i for i in pivo_uf.columns if i[0] == "participantes virtuais"
        ]
        if ix_eventos_presenciais:
            pivo_uf[("nº eventos presenciais", "total")] = pivo_uf[
                ix_eventos_presenciais
            ].sum(axis=1)
            ix_eventos_presenciais.append(("nº eventos presenciais", "total"))
        if ix_eventos_virtuais:
            pivo_uf[("nº eventos virtuais", "total")] = pivo_uf[
                ix_eventos_virtuais
            ].sum(axis=1)
            ix_eventos_virtuais.append(("nº eventos virtuais", "total"))
        if ix_participantes_presenciais:
            pivo_uf[("participantes presenciais", "total")] = pivo_uf[
                ix_participantes_presenciais
            ].sum(axis=1)
            ix_participantes_presenciais.append(
                ("participantes presenciais", "total")
            )
        if ix_participantes_virtuais:
            pivo_uf[("participantes virtuais", "total")] = pivo_uf[
                ix_participantes_virtuais
            ].sum(axis=1)
            ix_participantes_virtuais.append(
                ("participantes virtuais", "total")
            )
        pivo_uf = pivo_uf[
            ix_eventos_presenciais
            + ix_eventos_virtuais
            + ix_participantes_presenciais
            + ix_participantes_virtuais
        ]
    # Cria tabela pivot das regiões
    pivo_regiao = df.pivot_table(
        index="regiao",
        columns="categoria",
        aggfunc=aggfuncs,
        fill_value=0,
    )
    # Calcula os totais de eventos e participantes para as regiões
    if len(categorias) > 1:
        ix_eventos_presenciais = [
            i for i in pivo_regiao.columns if i[0] == "nº eventos presenciais"
        ]
        ix_eventos_virtuais = [
            i for i in pivo_regiao.columns if i[0] == "nº eventos virtuais"
        ]
        ix_participantes_presenciais = [
            i
            for i in pivo_regiao.columns
            if i[0] == "participantes presenciais"
        ]
        ix_participantes_virtuais = [
            i for i in pivo_regiao.columns if i[0] == "participantes virtuais"
        ]
        if ix_eventos_presenciais:
            pivo_regiao[("nº eventos presenciais", "total")] = pivo_regiao[
                ix_eventos_presenciais
            ].sum(axis=1)
            ix_eventos_presenciais.append(("nº eventos presenciais", "total"))
        if ix_eventos_virtuais:
            pivo_regiao[("nº eventos virtuais", "total")] = pivo_regiao[
                ix_eventos_virtuais
            ].sum(axis=1)
            ix_eventos_virtuais.append(("nº eventos virtuais", "total"))
        if ix_participantes_presenciais:
            pivo_regiao[("participantes presenciais", "total")] = pivo_regiao[
                ix_participantes_presenciais
            ].sum(axis=1)
            ix_participantes_presenciais.append(
                ("participantes presenciais", "total")
            )
        if ix_participantes_virtuais:
            pivo_regiao[("participantes virtuais", "total")] = pivo_regiao[
                ix_participantes_virtuais
            ].sum(axis=1)
            ix_participantes_virtuais.append(
                ("participantes virtuais", "total")
            )
        pivo_regiao = pivo_regiao[
            ix_eventos_presenciais
            + ix_eventos_virtuais
            + ix_participantes_presenciais
            + ix_participantes_virtuais
        ]
    # Cabeçalhos para impressão
    cabecalho_uf = [
        (k, [i[1] for i in v])
        for k, v in groupby(pivo_uf.columns, lambda x: x[0])
    ]
    cabecalho_regiao = [
        (k, [i[1] for i in v])
        for k, v in groupby(pivo_regiao.columns, lambda x: x[0])
    ]
    # Fixar tudo em int
    pivo_uf = pivo_uf.astype(int)
    pivo_regiao = pivo_regiao.astype(int)
    # Imprimir
    context = {
        "form": form,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "categorias": [
            c[1] for c in TipoEvento.CATEGORIA_CHOICES if c[0] in categorias
        ],
        "virtual": [
            m[1] for m in EventosPorUfForm.MODO_CHOICES if m[0] in virtual
        ],
        "pivo_uf": pivo_uf,
        "pivo_regiao": pivo_regiao,
        "cabecalho_uf": cabecalho_uf,
        "cabecalho_regiao": cabecalho_regiao,
        "total_uf": pivo_uf.sum(),
        "total_regiao": pivo_regiao.sum(),
    }
    if formato == "pdf":
        context["title"] = _("Eventos por Unidade da Federação")
        context["pdf"] = True
        return WeasyTemplateResponse(
            filename=f"eventos_por_uf-{data_inicio}-{data_fim}.pdf",
            request=request,
            template="eventos/eventos_por_uf_pdf.html",
            context=context,
            content_type="application/pdf",
        )
    elif formato == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="eventos_por_uf-{data_inicio}-{data_fim}.csv"'
        )
        pivo_uf.to_csv(response)
        return response
    return render(request, "eventos/eventos_por_uf.html", context=context)


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
