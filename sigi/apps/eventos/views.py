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
from django.db import models
from django.db.models import (
    Avg,
    Case,
    Count,
    F,
    Max,
    Min,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
    Sum,
    Value,
    When,
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
    CalendarioForm,
)
from sigi.apps.eventos.serializers import (
    EventoSerializer,
    EventoListSerializer,
)
from sigi.apps.servidores.models import Servidor
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

    def get_dataset(self, context):
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



class CalendarioReportView(LoginRequiredMixin, UserPassesTestMixin, ReportListView):
    title = _("Calendário de eventos")
    filter_form = CalendarioForm
    template_name = "eventos/calendario.html"
    template_name_pdf = "eventos/calendario_pdf.html"
    
    
    list_fields = []
    list_labels = []
    
    def get_list_labels(self):
        
        return []
    
    def test_func(self):
        return self.request.user.is_staff

    def get_initial(self):
        return {
            "mes_ano": timezone.localdate().replace(day=1),
            "categorias": [c[0] for c in TipoEvento.CATEGORIA_CHOICES],
            "status": [s[0] for s in Evento.STATUS_CHOICES],
        }

    def get_queryset(self):
        
        return Evento.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if "mes_ano" in self.request.GET:
            form = CalendarioForm(self.request.GET)
        else:
            form = CalendarioForm(initial=self.get_initial())
        context["form"] = form

        if not form.is_valid():
            return context

        mes_pesquisa = form.cleaned_data["mes_ano"].month
        ano_pesquisa = form.cleaned_data["mes_ano"].year
        sel_categorias = form.cleaned_data["categorias"]
        sel_status = form.cleaned_data["status"]

        
        lang = to_locale(get_language()) + ".UTF-8"
        locale.setlocale(locale.LC_ALL, lang)

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

        semanas = [
            {"datas": s, "eventos": []}
            for s in calendar.Calendar().monthdatescalendar(ano_pesquisa, mes_pesquisa)
        ]

        for e in eventos:
            for s in semanas:
                
                if not (e.data_termino < s["datas"][0] or e.data_inicio > s["datas"][-1]):
                    start = max(s["datas"][0], e.data_inicio)
                    end = min(s["datas"][-1], e.data_termino)
                    s["eventos"].append((
                        e,
                        (
                            start.weekday(),
                            end.weekday() - start.weekday() + 1,
                            6 - end.weekday(),
                        ),
                    ))

        context.update({
            "ano_pesquisa": ano_pesquisa,
            "mes_pesquisa": mes_pesquisa,
            "sel_categorias": sel_categorias,
            "sel_status": sel_status,
            "day_names": calendar.day_abbr,
            "categorias": TipoEvento.CATEGORIA_CHOICES,
            "status": Evento.STATUS_CHOICES,
            "eventos": eventos,
            "semanas": semanas,
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        fmt = self.request.GET.get("fmt", "html")
        if fmt == "pdf":
            context["title"] = _("Calendário de eventos")
            context["pdf"] = True
            return WeasyTemplateResponse(
                filename=f"calendario_{context.get('ano_pesquisa'):04}{context.get('mes_pesquisa'):02}.pdf",
                request=self.request,
                template=self.template_name_pdf,
                context=context,
                content_type="application/pdf",
            )
        return super().render_to_response(context, **response_kwargs)

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

class AlocacaoEquipeReportView(LoginRequiredMixin, UserPassesTestMixin, ReportListView):
    title = _("Alocação de equipe")
    template_name = "eventos/alocacao_equipe.html"
    template_name_pdf = "eventos/alocacao_equipe_pdf.html"
    
    
    list_fields = []
    list_labels = []

    def test_func(self):
        """Restringe o acesso a usuários staff."""
        return self.request.user.is_staff

    def get_list_labels(self):
        """Sobrescreve para não exigir listagem de campos."""
        return []

    def get_queryset(self):
        """Retorna um queryset vazio, pois toda a lógica está em get_context_data."""
        return Evento.objects.none()

    def get_context_data(self, **kwargs):
        """Reproduz a lógica original da FBV, populando o contexto com dados."""
        context = super().get_context_data(**kwargs)
        
        
        ano_pesquisa = int(self.request.GET.get("ano", timezone.localdate().year))
        mes_pesquisa = int(self.request.GET.get("mes", 0))
        semana_pesquisa = int(self.request.GET.get("semana", 0))
        formato = self.request.GET.get("fmt", "html")

        
        lang = to_locale(get_language()) + ".UTF-8"
        locale.setlocale(locale.LC_ALL, lang)

        
        eventos = (
            Evento.objects.exclude(
                status__in=(Evento.STATUS_CANCELADO, Evento.STATUS_SOBRESTADO)
            )
            .prefetch_related("equipe_set")
        )

        num_cols = 12  

        
        if mes_pesquisa > 0:
            semanas = [
                [s[0], s[-1]]
                for s in calendar.Calendar().monthdatescalendar(ano_pesquisa, mes_pesquisa)
            ]
            num_cols = len(semanas)
            if semana_pesquisa > 0:
                
                dias = calendar.Calendar().monthdatescalendar(ano_pesquisa, mes_pesquisa)[semana_pesquisa - 1]
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

        
        dados = []
        for evento in eventos:
            for equipe in evento.equipe_set.all():
                registro = None
                
                for r in dados:
                    if r[0] == equipe.membro.pk:
                        registro = r
                        break
                
                if not registro:
                    if semana_pesquisa > 0:
                        registro = [
                            equipe.membro.pk,
                            equipe.membro.get_apelido(),
                            OrderedDict([(dia, []) for dia in dias]),
                        ]
                    else:
                        registro = [
                            equipe.membro.pk,
                            equipe.membro.get_apelido(),
                            [{"dias": 0, "eventos": 0} for __ in range(num_cols)],
                        ]
                    dados.append(registro)

                
                if mes_pesquisa > 0:
                    if semana_pesquisa > 0:
                        for dia in dias:
                            if evento.data_inicio <= dia <= evento.data_termino:
                                registro[2][dia].append(evento)
                    else:
                        for idx, (inicio, fim) in enumerate(semanas):
                            
                            if inicio <= evento.data_inicio <= fim:
                                registro[2][idx]["dias"] += (
                                    min(fim, evento.data_termino) - evento.data_inicio
                                ).days + 1
                                registro[2][idx]["eventos"] += 1
                            
                            elif inicio <= evento.data_termino <= fim:
                                registro[2][idx]["dias"] += (
                                    min(fim, evento.data_termino) - evento.data_inicio
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
                [registro[1]] + list(registro[2].values()) 
                for registro in dados
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
                row = [r[1]]
                for d in r[2]:
                    if d["dias"] > 0 or d["eventos"] > 0:
                        
                        texto = (
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
                        )
                        row.append(texto)
                    else:
                        row.append("")
                linhas.append(row)

        
        context.update({
            "anos": (
                Evento.objects.exclude(data_inicio=None)
                .order_by("data_inicio__year")
                .distinct("data_inicio__year")
                .values_list("data_inicio__year", flat=True)
            ),
            "ano_pesquisa": ano_pesquisa,
            "linhas": linhas,
            "meses": meses,
        })

        
        if mes_pesquisa > 0:
            context["mes_pesquisa"] = mes_pesquisa
            
            semanas = [
                [s[0], s[-1]]
                for s in calendar.Calendar().monthdatescalendar(ano_pesquisa, mes_pesquisa)
            ]
            context["semanas"] = [
                _(f"de {inicio:%d/%m} a {fim:%d/%m}") 
                for inicio, fim in semanas
            ]
            if semana_pesquisa > 0:
                
                context["semana_pesquisa"] = semana_pesquisa
                context["eventos"] = eventos
                cabecalho = [_("Servidor")] + list(dias)
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
        context["formato"] = formato  

        return context

    def render_to_response(self, context, **response_kwargs):
        """Decide se retorna HTML, PDF ou CSV."""
        fmt = context.get("formato", "html")
        if fmt == "pdf":
            context["pdf"] = True
            context["title"] = self.title
            ano_pesquisa = context.get("ano_pesquisa", timezone.localdate().year)
            return WeasyTemplateResponse(
                filename=f"alocacao_equipe_{ano_pesquisa}.pdf",
                request=self.request,
                template=self.template_name_pdf,
                context=context,
                content_type="application/pdf",
            )
        elif fmt == "csv":
            ano_pesquisa = context.get("ano_pesquisa", timezone.localdate().year)
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="alocacao_equipe_{ano_pesquisa}.csv"'
            writer = csv.writer(response)
            writer.writerow(context["cabecalho"])
            writer.writerows(context["linhas"])
            return response
        
        return super().render_to_response(context, **response_kwargs)


class EventosPorUfReportView(LoginRequiredMixin, UserPassesTestMixin, ReportListView):
    title = _("Eventos por UF")
    filter_form = EventosPorUfForm
    template_name = "eventos/eventos_por_uf.html"
    template_name_pdf = "eventos/eventos_por_uf_pdf.html"
    
    
    list_fields = []  
    list_labels = []

    def get_list_labels(self):
        
        return []

    def test_func(self):
        return self.request.user.is_staff

    def get_initial(self):
        return {
            "data_inicio": datetime.date.today().replace(day=1),
            "data_fim": datetime.date.today().replace(
                day=calendar.monthrange(
                    datetime.date.today().year, datetime.date.today().month
                )[1]
            ),
            "categoria": [c[0] for c in TipoEvento.CATEGORIA_CHOICES],
            "virtual": [m[0] for m in EventosPorUfForm.MODO_CHOICES],
        }

    def get_queryset(self):
        
        return UnidadeFederativa.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_filter_form_instance()
        context["form"] = form
        if not form.is_valid():
            return context

        
        data_inicio = form.cleaned_data.get("data_inicio")
        data_fim = form.cleaned_data.get("data_fim")
        initial = self.get_initial()
        categorias = form.cleaned_data.get("categoria", initial["categoria"])
        virtual = form.cleaned_data.get("virtual", initial["virtual"])

        annotates = {}
        aggfuncs = {}
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
                municipio__orgao__evento__data_inicio__range=(data_inicio, data_fim),
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
            messages.error(
                self.request,
                _("Nenhum evento foi realizado no período solicitado")
            )
            return context

        
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
        for sigla, nome in UnidadeFederativa.REGIAO_CHOICES:
            df["regiao"].replace(sigla, nome, inplace=True)
        for cod, nome in TipoEvento.CATEGORIA_CHOICES:
            df["categoria"].replace(cod, nome, inplace=True)
        
        pivo_uf = df.pivot_table(
            index=["regiao", "nome"],
            columns="categoria",
            aggfunc=aggfuncs,
            fill_value=0,
        )
        if len(categorias) > 1:
            ix_eventos_presenciais = [i for i in pivo_uf.columns if i[0] == "nº eventos presenciais"]
            ix_eventos_virtuais = [i for i in pivo_uf.columns if i[0] == "nº eventos virtuais"]
            ix_participantes_presenciais = [i for i in pivo_uf.columns if i[0] == "participantes presenciais"]
            ix_participantes_virtuais = [i for i in pivo_uf.columns if i[0] == "participantes virtuais"]
            if ix_eventos_presenciais:
                pivo_uf[("nº eventos presenciais", "total")] = pivo_uf[ix_eventos_presenciais].sum(axis=1)
                ix_eventos_presenciais.append(("nº eventos presenciais", "total"))
            if ix_eventos_virtuais:
                pivo_uf[("nº eventos virtuais", "total")] = pivo_uf[ix_eventos_virtuais].sum(axis=1)
                ix_eventos_virtuais.append(("nº eventos virtuais", "total"))
            if ix_participantes_presenciais:
                pivo_uf[("participantes presenciais", "total")] = pivo_uf[ix_participantes_presenciais].sum(axis=1)
                ix_participantes_presenciais.append(("participantes presenciais", "total"))
            if ix_participantes_virtuais:
                pivo_uf[("participantes virtuais", "total")] = pivo_uf[ix_participantes_virtuais].sum(axis=1)
                ix_participantes_virtuais.append(("participantes virtuais", "total"))
            pivo_uf = pivo_uf[
                ix_eventos_presenciais + ix_eventos_virtuais +
                ix_participantes_presenciais + ix_participantes_virtuais
            ]
        
        pivo_regiao = df.pivot_table(
            index="regiao",
            columns="categoria",
            aggfunc=aggfuncs,
            fill_value=0,
        )
        if len(categorias) > 1:
            ix_eventos_presenciais = [i for i in pivo_regiao.columns if i[0] == "nº eventos presenciais"]
            ix_eventos_virtuais = [i for i in pivo_regiao.columns if i[0] == "nº eventos virtuais"]
            ix_participantes_presenciais = [i for i in pivo_regiao.columns if i[0] == "participantes presenciais"]
            ix_participantes_virtuais = [i for i in pivo_regiao.columns if i[0] == "participantes virtuais"]
            if ix_eventos_presenciais:
                pivo_regiao[("nº eventos presenciais", "total")] = pivo_regiao[ix_eventos_presenciais].sum(axis=1)
                ix_eventos_presenciais.append(("nº eventos presenciais", "total"))
            if ix_eventos_virtuais:
                pivo_regiao[("nº eventos virtuais", "total")] = pivo_regiao[ix_eventos_virtuais].sum(axis=1)
                ix_eventos_virtuais.append(("nº eventos virtuais", "total"))
            if ix_participantes_presenciais:
                pivo_regiao[("participantes presenciais", "total")] = pivo_regiao[ix_participantes_presenciais].sum(axis=1)
                ix_participantes_presenciais.append(("participantes presenciais", "total"))
            if ix_participantes_virtuais:
                pivo_regiao[("participantes virtuais", "total")] = pivo_regiao[ix_participantes_virtuais].sum(axis=1)
                ix_participantes_virtuais.append(("participantes virtuais", "total"))
            pivo_regiao = pivo_regiao[
                ix_eventos_presenciais + ix_eventos_virtuais +
                ix_participantes_presenciais + ix_participantes_virtuais
            ]
        
        cabecalho_uf = [
            (k, [i[1] for i in v])
            for k, v in groupby(pivo_uf.columns, lambda x: x[0])
        ]
        cabecalho_regiao = [
            (k, [i[1] for i in v])
            for k, v in groupby(pivo_regiao.columns, lambda x: x[0])
        ]
        
        pivo_uf = pivo_uf.astype(int)
        pivo_regiao = pivo_regiao.astype(int)
        
        context.update({
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "categorias": [c[1] for c in TipoEvento.CATEGORIA_CHOICES if c[0] in categorias],
            "virtual": [m[1] for m in EventosPorUfForm.MODO_CHOICES if m[0] in virtual],
            "pivo_uf": pivo_uf,
            "pivo_regiao": pivo_regiao,
            "cabecalho_uf": cabecalho_uf,
            "cabecalho_regiao": cabecalho_regiao,
            "total_uf": pivo_uf.sum(),
            "total_regiao": pivo_regiao.sum(),
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        fmt = self.request.GET.get("fmt", "html")
        if fmt == "pdf":
            context["title"] = _("Eventos por Unidade da Federação")
            context["pdf"] = True
            return WeasyTemplateResponse(
                request=self.request,
                template=self.template_name_pdf,
                context=context,
                content_type="application/pdf",
            )
        elif fmt == "csv":
            response = HttpResponse(content_type="text/csv")
            data_inicio = context.get("data_inicio")
            data_fim = context.get("data_fim")
            response["Content-Disposition"] = (
                f'attachment; filename="eventos_por_uf-{data_inicio}-{data_fim}.csv"'
            )
            pivo_uf = context.get("pivo_uf")
            pivo_uf.to_csv(response)
            return response
        return super().render_to_response(context, **response_kwargs)

class SolicitacoesPorPeriodoReportView(LoginRequiredMixin, UserPassesTestMixin, ReportListView):
    title = _("Solicitações por período")
    filter_form = SolicitacoesPorPeriodoForm
    template_name = "eventos/solicitacoes_por_periodo.html"
    template_name_pdf = "eventos/solicitacoes_por_periodo_pdf.html"
    
    
    list_fields = []
    list_labels = []
    
    def get_list_labels(self):
        
        return []

    def test_func(self):
        return self.request.user.is_staff

    def get_initial(self):
        return {
            "data_inicio": datetime.date.today().replace(day=1),
            "data_fim": datetime.date.today().replace(
                day=calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1]
            ),
            "tipos_evento": TipoEvento.objects.all(),
            "virtual": [m[0] for m in SolicitacoesPorPeriodoForm.MODO_CHOICES],
            "status": [s[0] for s in Solicitacao.STATUS_CHOICES],
        }

    def get_queryset(self):
        
        return Solicitacao.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_filter_form_instance()
        context["form"] = form

        if not form.is_valid():
            return context

        data_inicio = form.cleaned_data.get("data_inicio")
        data_fim = form.cleaned_data.get("data_fim")
        initial = self.get_initial()
        tipos_evento = form.cleaned_data.get("tipos_evento", initial["tipos_evento"])
        virtual = form.cleaned_data.get("virtual", initial["virtual"])
        status = form.cleaned_data.get("status", initial["status"])

        
        sq_equipe = (
            Equipe.objects.order_by()
            .annotate(
                tot=Sum(F("qtde_diarias") * F("valor_diaria") + F("total_passagens"))
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
                    filter=Q(itemsolicitado__status=ItemSolicitado.STATUS_AUTORIZADO)
                ),
                qtde_rejeitadas=Count(
                    "itemsolicitado__id",
                    filter=Q(itemsolicitado__status=ItemSolicitado.STATUS_REJEITADO)
                ),
                participantes=Sum("itemsolicitado__evento__total_participantes"),
                custo_total=Subquery(
                    sq_equipe.filter(evento__itemsolicitado__solicitacao=OuterRef("pk"))[:1]
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

        resumo_uf = pd.DataFrame(
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
        ).rename(
            columns={
                "casa__municipio__uf__regiao": "regiao",
                "casa__municipio__uf__sigla": "uf",
            }
        )

        if resumo_uf.empty:
            resumo_regiao = resumo_uf
        else:
            resumo_uf = (
                resumo_uf.fillna(0)
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

        resumo_tipo_evento = pd.DataFrame(
            ItemSolicitado.objects.filter(solicitacao__in=solicitacoes)
            .order_by("tipo_evento__sigla", "tipo_evento__nome")
            .values("tipo_evento__sigla", "tipo_evento__nome")
            .annotate(
                qtde_solicitadas=Count("id"),
                qtde_atendidas=Count("id", filter=Q(status=ItemSolicitado.STATUS_AUTORIZADO)),
                qtde_rejeitadas=Count("id", filter=Q(status=ItemSolicitado.STATUS_REJEITADO)),
                participantes=Sum("evento__total_participantes"),
                custo_total=Subquery(
                    sq_equipe.filter(evento__itemsolicitado=OuterRef("pk"))[:1]
                ),
            )
        ).rename(
            columns={
                "tipo_evento__sigla": "sigla",
                "tipo_evento__nome": "nome",
            }
        )

        if not resumo_tipo_evento.empty:
            resumo_tipo_evento = (
                resumo_tipo_evento.groupby(["sigla", "nome"], as_index=False)
                .sum()
                .fillna(0)
            )
            resumo_tipo_evento["participantes"] = resumo_tipo_evento["participantes"].astype("int")
            resumo_tipo_evento.replace([0], [None], inplace=True)

        context.update({
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "status_choices": ItemSolicitado.STATUS_CHOICES,
            "legenda_oficinas": legenda_oficinas,
            "tipos_evento": tipos_evento,
            "virtual": [m[1] for m in SolicitacoesPorPeriodoForm.MODO_CHOICES if m[0] in virtual],
            "solicitacoes": solicitacoes,
            "sumario": sumario,
            "resumo_uf": resumo_uf,
            "resumo_regiao": resumo_regiao,
            "resumo_tipo_evento": resumo_tipo_evento,
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        formato = self.request.GET.get("fmt", "html")
        if formato == "pdf":
            context["pdf"] = True
            return WeasyTemplateResponse(
                filename=f"solicitacoes_por_periodo-{context.get('data_inicio')}-{context.get('data_fim')}.pdf",
                request=self.request,
                template=self.template_name_pdf,
                context=context,
                content_type="application/pdf",
            )
        elif formato == "csv":
            response = HttpResponse(content_type="text/csv")
            data_inicio = context.get("data_inicio")
            data_fim = context.get("data_fim")
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
            writer.writerows(context["solicitacoes"].values(*fieldnames))
            return response
        return super().render_to_response(context, **response_kwargs)

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


class CustosEventosReport(
    LoginRequiredMixin, UserPassesTestMixin, ReportListView
):
    title = _("Custos por eventos")
    template_name = "admin/eventos/custos_eventos_report.html"
    template_name_pdf = "admin/eventos/custos_eventos_report_pdf.html"
    filter_form = EventosPorUfForm
    queryset = Evento.objects.filter(status=Evento.STATUS_REALIZADO)
    list_fields = [
        "nome",
        "data_inicio",
        "data_termino",
        "turma",
        "descricao",
        "virtual",
        "solicitante",
        "num_processo",
        "casa_anfitria__nome",
        "casa_anfitria__municipio__nome",
        "casa_anfitria__municipio__uf__sigla",
        "duracao_dias",
        "qtde_diarias",
        "vlr_tot_diarias",
        "custo_total",
        "custo_medio_participante",
        "custo_medio_membro",
        "tot_membros",
    ]

    def test_func(self):
        return self.request.user.is_staff

    def filter_queryset(self, queryset):
        form = self.get_filter_form_instance()
        if form.is_valid():
            data_inicio = form.cleaned_data.get("data_inicio")
            data_fim = form.cleaned_data.get("data_fim")
            categorias = form.cleaned_data.get(
                "categoria", [c[0] for c in TipoEvento.CATEGORIA_CHOICES]
            )
            modo = form.cleaned_data.get("virtual", ["V", "P"])
            queryset = queryset.filter(
                status=Evento.STATUS_REALIZADO,
                data_inicio__gte=data_inicio,
                data_termino__lte=data_fim,
                tipo_evento__categoria__in=categorias,
            )
            if len(modo) == 1:
                if "V" in modo:
                    queryset = queryset.filter(virtual=True)
                else:
                    queryset = queryset.filter(virtual=False)
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        form = self.get_filter_form_instance()
        if queryset.exists():
            context = context_custos_eventos(queryset)
            form.is_valid()
            context["data_inicio"] = form.cleaned_data["data_inicio"]
            context["data_fim"] = form.cleaned_data["data_fim"]
        else:
            context = {"object_list": False}
        context["form"] = form
        context["report_title"] = self.get_title()
        return context

    def get_dataset(self, context):
        dataset = context["eventos"]
        return dataset.values(*self.list_fields), self.list_fields


class CustosServidorReport(
    LoginRequiredMixin, UserPassesTestMixin, ReportListView
):
    title = _("Custos por servidor")
    template_name = "admin/eventos/custos_servidor_report.html"
    template_name_pdf = "admin/eventos/custos_servidor_report_pdf.html"
    filter_form = EventosPorUfForm
    queryset = Evento.objects.filter(status=Evento.STATUS_REALIZADO)

    def test_func(self):
        return self.request.user.is_staff

    def filter_queryset(self, queryset):
        form = self.get_filter_form_instance()
        if form.is_valid():
            data_inicio = form.cleaned_data.get("data_inicio")
            data_fim = form.cleaned_data.get("data_fim")
            categorias = form.cleaned_data.get(
                "categoria", [c[0] for c in TipoEvento.CATEGORIA_CHOICES]
            )
            modo = form.cleaned_data.get("virtual", ["V", "P"])
            queryset = queryset.filter(
                status=Evento.STATUS_REALIZADO,
                data_inicio__gte=data_inicio,
                data_termino__lte=data_fim,
                tipo_evento__categoria__in=categorias,
            )
            if len(modo) == 1:
                if "V" in modo:
                    queryset = queryset.filter(virtual=True)
                else:
                    queryset = queryset.filter(virtual=False)
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        form = self.get_filter_form_instance()
        if queryset.exists():
            context = context_custos_servidor(queryset)
            form.is_valid()
            context["data_inicio"] = form.cleaned_data["data_inicio"]
            context["data_fim"] = form.cleaned_data["data_fim"]
        else:
            context = {}
        context["form"] = form
        return context

    def render_to_response(self, context, **response_kwargs):
        if self._is_csv():
            dataset = context["servidores"]
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{self.get_filename()}.csv"'
            )
            dataset.to_csv(response, index=False, encoding="utf8")
            return response
        return super().render_to_response(context, **response_kwargs)


def context_custos_eventos(queryset):
    my_decimal_field = models.DecimalField(max_digits=14, decimal_places=2)
    equipe_qs = Equipe.objects.annotate(
        total_diarias=(F("qtde_diarias") * F("valor_diaria")),
        antecedencia=models.functions.ExtractDay(
            F("evento__data_inicio") - F("emissao_passagens")
        ),
    )
    eventos = queryset.annotate(
        duracao_dias=(
            models.functions.ExtractDay(F("data_termino") - F("data_inicio"))
            + 1
        ),
        qtde_diarias=Sum("equipe__qtde_diarias"),
        vlr_tot_diarias=Sum(
            F("equipe__qtde_diarias") * F("equipe__valor_diaria"),
            output_field=my_decimal_field,
        ),
        vlr_tot_passagens=Sum("equipe__total_passagens"),
        custo_total=F("vlr_tot_diarias") + F("vlr_tot_passagens"),
        custo_medio_participante=models.functions.Cast(
            Case(
                When(total_participantes__lte=0, then=0),
                default=F("custo_total") / F("total_participantes"),
                output_field=my_decimal_field,
            ),
            output_field=my_decimal_field,
        ),
        custo_medio_membro=models.functions.Cast(
            F("custo_total") / Count("equipe__membro"),
            output_field=my_decimal_field,
        ),
        tot_membros=Count("equipe"),
    ).prefetch_related(
        Prefetch("equipe_set", queryset=equipe_qs, to_attr="equipe_ext")
    )
    resumo = eventos.aggregate(
        qtde_oficinas=Count("id"),
        tot_participantes=Sum("total_participantes"),
        media_participantes=models.functions.Cast(
            1.0 * F("tot_participantes") / F("qtde_oficinas"),
            output_field=my_decimal_field,
        ),
        min_participantes=Min("total_participantes"),
        max_participantes=Max("total_participantes"),
        tot_servidores=Sum("tot_membros"),
        media_membros=models.functions.Cast(
            1.0 * Sum("tot_membros") / F("qtde_oficinas"),
            output_field=my_decimal_field,
        ),
        min_membros=Min("tot_membros"),
        max_membros=Max("tot_membros"),
        tot_dias=Sum("duracao_dias"),
        media_dias=models.functions.Cast(
            1.0 * F("tot_dias") / F("qtde_oficinas"),
            output_field=my_decimal_field,
        ),
        tot_diarias=Sum("qtde_diarias"),
        media_diarias=models.functions.Cast(
            1.0 * F("tot_diarias") / F("qtde_oficinas"),
            output_field=my_decimal_field,
        ),
        tot_custo_total=Sum("custo_total"),
        tot_custo_diarias=Sum("vlr_tot_diarias"),
        tot_custo_passagens=Sum("vlr_tot_passagens"),
        media_custo_total=models.functions.Cast(
            F("tot_custo_total") / F("qtde_oficinas"),
            output_field=my_decimal_field,
        ),
        media_custo_diarias=models.functions.Cast(
            F("tot_custo_diarias") / F("qtde_oficinas"),
            output_field=my_decimal_field,
        ),
        media_custo_passagens=models.functions.Cast(
            F("tot_custo_passagens") / F("qtde_oficinas"),
            output_field=my_decimal_field,
        ),
        media_custo_participantes=models.functions.Cast(
            F("tot_custo_total") / F("tot_participantes"),
            output_field=my_decimal_field,
        ),
        media_custo_membro=models.functions.Cast(
            F("tot_custo_total") / Sum("tot_membros"),
            output_field=my_decimal_field,
        ),
    )
    resumo.update(
        eventos.aggregate(
            media_antecedencia=Avg(
                models.functions.ExtractDay(
                    F("data_inicio") - F("equipe__emissao_passagens")
                )
            ),
            min_antecedencia=Min(
                models.functions.ExtractDay(
                    F("data_inicio") - F("equipe__emissao_passagens")
                )
            ),
            max_antecedencia=Max(
                models.functions.ExtractDay(
                    F("data_inicio") - F("equipe__emissao_passagens")
                )
            ),
        )
    )

    f_valor_diarias = F("equipe__qtde_diarias") * F("equipe__valor_diaria")
    f_custo_total = (f_valor_diarias) + F("equipe__total_passagens")

    extrato = (
        queryset.order_by("casa_anfitria__municipio__uf__regiao")
        .annotate(
            regiao=F("casa_anfitria__municipio__uf__regiao"),
            tot_diarias=Sum(f_valor_diarias),
            tot_passagens=Sum("equipe__total_passagens"),
            tot_custo=Sum(f_custo_total),
        )
        .values("regiao", "tot_diarias", "tot_passagens", "tot_custo")
    )

    df = (
        pd.DataFrame(extrato)
        .set_index("regiao")
        .groupby("regiao")
        .aggregate(["sum", "min", "max", "mean"])
        .fillna(0)
    )

    custos_regiao = [
        {
            "nome": nome,
            "extrato": df.loc[sigla] if sigla in df.index else None,
        }
        for sigla, nome in UnidadeFederativa.REGIAO_CHOICES
    ]

    return {
        "eventos": eventos.order_by("data_inicio"),
        "resumo": resumo,
        "custos_regiao": custos_regiao,
        "report_title": _("Custos por eventos"),
        "object_list": True,
    }


def context_custos_servidor(queryset):
    equipe_qs = Equipe.objects.filter(evento__in=queryset)
    f_total_diarias = F("equipe_evento__qtde_diarias") * F(
        "equipe_evento__valor_diaria"
    )
    servidores = (
        (
            Servidor.objects.distinct()
            .filter(equipe_evento__evento__in=queryset)
            .prefetch_related(
                Prefetch(
                    "equipe_evento", queryset=equipe_qs, to_attr="equipe_ext"
                )
            )
            .annotate(
                qtde_eventos=Count("equipe_evento"),
                qtde_diarias=Sum("equipe_evento__qtde_diarias"),
                total_diarias=Sum(f_total_diarias),
                total_passagens=Sum("equipe_evento__total_passagens"),
                total_custo=Sum(
                    F("equipe_evento__total_passagens") + f_total_diarias
                ),
            )
        )
        .order_by("nome_completo")
        .values(
            "nome_completo",
            "qtde_eventos",
            "qtde_diarias",
            "total_diarias",
            "total_passagens",
            "total_custo",
        )
    )
    servidores = pd.DataFrame(servidores)
    totais = servidores[
        [
            "qtde_eventos",
            "qtde_diarias",
            "total_diarias",
            "total_passagens",
            "total_custo",
        ]
    ].sum()
    servidores["media_diarias"] = (
        servidores["total_diarias"] / servidores["qtde_diarias"]
    )
    totais["media_diarias"] = totais["total_diarias"] / totais["qtde_diarias"]
    return {
        "object_list": True,
        "servidores": servidores.fillna(0),
        "totais": totais.fillna(0),
        "report_title": _("Custos por servidor"),
    }
