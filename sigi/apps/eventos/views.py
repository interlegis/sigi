import calendar
import csv
import datetime
import locale
import pandas as pd
from functools import reduce
from itertools import groupby
from rest_framework import generics
from typing import OrderedDict
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import (
    Count,
    Sum,
    Q,
    F,
    OuterRef,
    Subquery,
    Case,
    When,
    Value,
)
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import (
    to_locale,
    get_language,
    ngettext,
    gettext as _,
)
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView
from django_weasyprint.views import WeasyTemplateResponse
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.eventos.models import (
    TipoEvento,
    Evento,
    Equipe,
    Solicitacao,
    ItemSolicitado,
    ParticipantesEvento,
)
from sigi.apps.eventos.forms import (
    EventosPorUfForm,
    SolicitacoesPorPeriodoForm,
)
from sigi.apps.eventos.serializers import (
    EventoSerializer,
    EventoListSerializer,
)
from sigi.apps.utils.views import ReportListView


class AlunosPorUfReportView(
    LoginRequiredMixin, UserPassesTestMixin, ReportListView
):
    title = _("Alunos por UF")
    empty_message = _("Nenhum evento para os parâmetros solicitados")
    filter_form = EventosPorUfForm
    list_fields = ["evento__nome", "uf__sigla", "inscritos", "aprovados"]
    list_labels = [""]

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        form = self.get_filter_form_instance()
        queryset = ParticipantesEvento.objects.none()
        if form.is_valid():
            data_inicio = form.cleaned_data.get("data_inicio")
            data_fim = form.cleaned_data.get("data_fim")
            categorias = form.cleaned_data.get(
                "categoria", [c[0] for c in TipoEvento.CATEGORIA_CHOICES]
            )
            modo = form.cleaned_data.get("virtual", ["V", "P"])
            queryset = ParticipantesEvento.objects.filter(
                evento__status=Evento.STATUS_REALIZADO,
                evento__data_inicio__gte=data_inicio,
                evento__data_termino__lte=data_fim,
                evento__tipo_evento__categoria__in=categorias,
            )
            if len(modo) == 1:
                if "V" in modo:
                    queryset = queryset.filter(evento__virtual=True)
                else:
                    queryset = queryset.filter(evento__virtual=False)
        return queryset

    def get_dataset(self):
        queryset = self.get_queryset()
        fieldnames = [
            "evento__nome",
            "evento__virtual",
            "uf__nome",
            "uf__sigla",
            "uf__regiao",
            "inscritos",
            "aprovados",
        ]
        queryset = queryset.values(*fieldnames)
        return queryset, fieldnames

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        if queryset:
            uf_sigla = Case(
                When(uf__sigla=None, then=Value("*")), default="uf__sigla"
            )
            uf_regiao = Case(
                *[
                    When(uf__regiao=r[0], then=Value(r[1]))
                    for r in UnidadeFederativa.REGIAO_CHOICES
                ],
                default=Value("*"),
            )
            modo = Case(
                When(evento__virtual=True, then=Value("Virtual")),
                default=Value("Presencial"),
            )

            df = pd.DataFrame(
                queryset.order_by("evento", "uf").values(
                    "evento__nome",
                    "inscritos",
                    "aprovados",
                    uf_sigla=uf_sigla,
                    modo=modo,
                )
            )
            context["inscritos_uf"] = df.pivot_table(
                values="inscritos",
                index=["evento__nome", "modo"],
                columns="uf_sigla",
                aggfunc="sum",
                margins=True,
                margins_name="Total",
                sort=True,
                fill_value=0,
            ).astype(pd.Int64Dtype())
            context["aprovados_uf"] = df.pivot_table(
                values="aprovados",
                index=["evento__nome", "modo"],
                columns="uf_sigla",
                aggfunc="sum",
                margins=True,
                margins_name="Total",
                sort=True,
                fill_value=0,
            ).astype(pd.Int64Dtype())
            df = pd.DataFrame(
                queryset.order_by("evento", "uf__regiao").values(
                    "evento__nome",
                    "inscritos",
                    "aprovados",
                    uf_regiao=uf_regiao,
                    modo=modo,
                )
            )
            context["inscritos_regiao"] = df.pivot_table(
                values="inscritos",
                index=["evento__nome", "modo"],
                columns="uf_regiao",
                aggfunc="sum",
                margins=True,
                margins_name="Total",
                sort=True,
                fill_value=0,
            ).astype(pd.Int64Dtype())
            context["aprovados_regiao"] = df.pivot_table(
                values="aprovados",
                index=["evento__nome", "modo"],
                columns="uf_regiao",
                aggfunc="sum",
                margins=True,
                margins_name="Total",
                sort=True,
                fill_value=0,
            ).astype(pd.Int64Dtype())
        return context


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


@login_required
@staff_member_required
def solicitacoes_por_periodo(request):
    formato = request.GET.get("fmt", "html")
    initials = {
        "data_inicio": datetime.date.today().replace(day=1),
        "data_fim": datetime.date.today().replace(
            day=calendar.monthrange(
                datetime.date.today().year, datetime.date.today().month
            )[1]
        ),
        "tipos_evento": TipoEvento.objects.all(),
        "virtual": [m[0] for m in SolicitacoesPorPeriodoForm.MODO_CHOICES],
        "status": [s[0] for s in Solicitacao.STATUS_CHOICES],
    }
    if "data_inicio" in request.GET or "data_fim" in request.GET:
        form = SolicitacoesPorPeriodoForm(request.GET)
    else:
        form = SolicitacoesPorPeriodoForm(initial=initials)
    if not form.is_valid():
        return render(
            request,
            "eventos/solicitacoes_por_periodo.html",
            context={"form": form},
        )
    data_inicio = form.cleaned_data.get("data_inicio")
    data_fim = form.cleaned_data.get("data_fim")
    tipos_evento = form.cleaned_data.get(
        "tipos_evento", initials["tipos_evento"]
    )
    virtual = form.cleaned_data.get("virtual", initials["virtual"])
    status = form.cleaned_data.get("status", initials["status"])

    sq_equipe = (
        Equipe.objects.order_by()
        .annotate(
            tot=Sum(
                F("qtde_diarias") * F("valor_diaria") + F("total_passagens")
            )
        )
        .values("tot")
    )
    sq_equipe.query.group_by = []
    solicitacoes = Solicitacao.objects.order_by().filter(
        data_pedido__range=(data_inicio, data_fim),
        itemsolicitado__tipo_evento__in=tipos_evento,
        itemsolicitado__virtual__in=virtual,
        status__in=status,
    )
    legenda_oficinas = (
        solicitacoes.order_by("itemsolicitado__tipo_evento__sigla")
        .values_list(
            "itemsolicitado__tipo_evento__sigla",
            "itemsolicitado__tipo_evento__nome",
        )
        .distinct()
    )
    solicitacoes = (
        solicitacoes.order_by(
            "casa__municipio__uf__regiao",
            "data_pedido",
            "casa__municipio__uf",
            "senador",
        )
        .annotate(
            qtde_solicitadas=Count("itemsolicitado__id"),
            qtde_atendidas=Count(
                "itemsolicitado__id",
                filter=Q(
                    itemsolicitado__status=ItemSolicitado.STATUS_AUTORIZADO
                ),
            ),
            qtde_rejeitadas=Count(
                "itemsolicitado__id",
                filter=Q(
                    itemsolicitado__status=ItemSolicitado.STATUS_REJEITADO
                ),
            ),
            participantes=Sum("itemsolicitado__evento__total_participantes"),
            custo_total=Subquery(
                sq_equipe.filter(
                    evento__itemsolicitado__solicitacao=OuterRef("pk")
                )[:1]
            ),
        )
        .select_related(
            "casa",
            "casa__municipio",
            "casa__municipio__uf",
            "casa__municipio__microrregiao",
        )
        .prefetch_related("itemsolicitado_set")
    )
    sumario = solicitacoes.aggregate(
        Sum("qtde_solicitadas"),
        Sum("qtde_atendidas"),
        Sum("qtde_rejeitadas"),
        Sum("participantes"),
        Sum("custo_total"),
    ).values()
    resumo_uf = (
        pd.DataFrame(
            solicitacoes.order_by(
                "casa__municipio__uf__regiao",
                "senador",
                "casa__municipio__uf",
            ).values(
                "casa__municipio__uf__regiao",
                "casa__municipio__uf__sigla",
                "senador",
                "qtde_solicitadas",
                "qtde_atendidas",
                "qtde_rejeitadas",
                "participantes",
                "custo_total",
            )
        )
        .rename(
            columns={
                "casa__municipio__uf__regiao": "regiao",
                "casa__municipio__uf__sigla": "uf",
            }
        )
        .fillna(0)
        .replace({"regiao": dict(UnidadeFederativa.REGIAO_CHOICES)})
        .groupby(["regiao", "senador", "uf"], as_index=False)
        .sum()
    )
    resumo_uf["participantes"] = resumo_uf["participantes"].astype("int")
    resumo_regiao = resumo_uf.groupby(["regiao"], as_index=False)[
        [
            "qtde_solicitadas",
            "qtde_atendidas",
            "qtde_rejeitadas",
            "participantes",
            "custo_total",
        ]
    ].sum()
    resumo_uf.replace([0], [None], inplace=True)
    resumo_regiao.replace([0], [None], inplace=True)
    resumo_tipo_evento = (
        pd.DataFrame(
            ItemSolicitado.objects.filter(solicitacao__in=solicitacoes)
            .order_by("tipo_evento__sigla", "tipo_evento__nome")
            .values("tipo_evento__sigla", "tipo_evento__nome")
            .annotate(
                qtde_solicitadas=Count("id"),
                qtde_atendidas=Count(
                    "id", filter=Q(status=ItemSolicitado.STATUS_AUTORIZADO)
                ),
                qtde_rejeitadas=Count(
                    "id", filter=Q(status=ItemSolicitado.STATUS_REJEITADO)
                ),
                participantes=Sum("evento__total_participantes"),
                custo_total=Subquery(
                    sq_equipe.filter(evento__itemsolicitado=OuterRef("pk"))[:1]
                ),
            )
        )
        .rename(
            columns={
                "tipo_evento__sigla": "sigla",
                "tipo_evento__nome": "nome",
            }
        )
        .groupby(["sigla", "nome"], as_index=False)
        .sum()
        .fillna(0)
    )
    resumo_tipo_evento["participantes"] = resumo_tipo_evento[
        "participantes"
    ].astype("int")
    resumo_tipo_evento.replace([0], [None], inplace=True)
    # Imprimir
    context = {
        "form": form,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "status_choices": ItemSolicitado.STATUS_CHOICES,
        "legenda_oficinas": legenda_oficinas,
        "tipos_evento": tipos_evento,
        "virtual": [
            m[1]
            for m in SolicitacoesPorPeriodoForm.MODO_CHOICES
            if m[0] in virtual
        ],
        "solicitacoes": solicitacoes,
        "sumario": sumario,
        "resumo_uf": resumo_uf,
        "resumo_regiao": resumo_regiao,
        "resumo_tipo_evento": resumo_tipo_evento,
    }
    if formato == "pdf":
        context["title"] = _("Solicitações por período")
        context["pdf"] = True
        return WeasyTemplateResponse(
            filename=f"solicitacoes_por_periodo-{data_inicio}-{data_fim}.pdf",
            request=request,
            template="eventos/solicitacoes_por_periodo_pdf.html",
            context=context,
            content_type="application/pdf",
        )
    elif formato == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="solicitacoes_por_periodo-{data_inicio}-{data_fim}.csv"'
        )
        fieldnames = [
            "id",
            "casa__nome",
            "casa__municipio__microrregiao__nome",
            "casa__municipio__uf__sigla",
            "casa__municipio__uf__regiao",
            "senador",
            "data_pedido",
            "qtde_solicitadas",
            "qtde_atendidas",
            "qtde_rejeitadas",
            "participantes",
            "custo_total",
        ]
        writer = csv.DictWriter(response, fieldnames)
        writer.writeheader()
        writer.writerows(solicitacoes.values(*fieldnames))
        return response
    return render(
        request, "eventos/solicitacoes_por_periodo.html", context=context
    )


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
