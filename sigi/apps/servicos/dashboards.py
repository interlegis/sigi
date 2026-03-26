import calendar
import datetime
import locale
from dashboard import Dashcard, getcolor
from random import choice, randint, seed
from urllib.parse import urlencode
from django.db.models import Count, F, Q
from django.db.models.functions import TruncMonth
from django.http import QueryDict
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _, to_locale, get_language
import django_filters
from sigi.apps.servicos.models import Servico, TipoServico
from sigi.apps.contatos.models import UnidadeFederativa


class UsoServicosFilter(django_filters.FilterSet):
    uf = django_filters.ModelChoiceFilter(
        field_name="servico__casa_legislativa__municipio__uf",
        label=_("UF"),
        queryset=UnidadeFederativa.objects.all(),
    )

    class Meta:
        model = TipoServico
        fields = ["uf"]


def get_anos_servico():
    return (
        (ano, str(ano))
        for ano in Servico.objects.filter(hospedagem_interlegis=True)
        .order_by("data_ativacao__year")
        .values_list("data_ativacao__year", flat=True)
        .distinct("data_ativacao__year")
    )


class AnoServicoFilter(django_filters.FilterSet):

    ano = django_filters.ChoiceFilter(
        field_name="data_ativacao",
        lookup_expr="year",
        label=_("Ano"),
        choices=get_anos_servico,
        empty_label=_("Todos os anos"),
    )

    class Meta:
        model = Servico
        fields = ["ano"]


class Sazonalidade(Dashcard):
    title = _("Sazonalidade da hospedagem de serviços")
    chart_type = Dashcard.TYPE_LINE
    model = Servico
    label_field = ("data_ativacao", TruncMonth, lambda d: d.strftime("%m/%Y"))
    datasets = [
        {
            "label_field": "tipo_servico__sigla",
            "data_field": ("*", Count),
        }
    ]

    def get_dataset_color(self, dataset_label):
        return getcolor(dataset_label)

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .filter(data_desativacao=None)
            .order_by("tipo_servico__sigla", "data_ativacao")
        )
        ano = request.GET.get("ano", None)
        if ano is None:
            ano = (
                qs.dates("data_ativacao", "year")
                .values_list("data_ativacao__year", flat=True)
                .last()
            )
        return qs.filter(data_ativacao__year=ano)

    def get_view_link(self, x_axis, y_axis, value):
        try:
            tipo = TipoServico.objects.get(sigla=x_axis)
        except TipoServico.DoesNotExist:
            return None
        mes, ano = y_axis.split("/")
        base_url = reverse("admin:servicos_servico_changelist")
        return (
            f"{base_url}?tipo_servico__id__exact={tipo.pk}"
            f"&data_ativacao__year={ano}&data_ativacao__month={mes}"
        )

    def get_prev_page(self, request=None, queryset=None):
        anos = Servico.objects.dates("data_ativacao", "year").values_list(
            "data_ativacao__year", flat=True
        )
        if request is None:
            params = QueryDict().copy()
            params["ano"] = anos.last() - 1
        else:
            params = request.GET.copy()
            params["ano"] = int(request.GET.get("ano", anos.last())) - 1
        if params["ano"] not in anos:
            return None
        return params.urlencode()

    def get_next_page(self, request=None, queryset=None):
        if request is None:
            return None
        anos = Servico.objects.dates("data_ativacao", "year").values_list(
            "data_ativacao__year", flat=True
        )
        params = request.GET.copy()
        params["ano"] = int(request.GET.get("ano", anos.last())) + 1
        if params["ano"] not in anos:
            return None
        return params.urlencode()


class ResumoSeit(Dashcard):
    title = _("Serviços hospedados no Interlegis")
    chart_type = Dashcard.TYPE_TABLE
    label_name = _("Serviço")
    model = Servico

    def get_meses(self, request=None):
        if request is None:
            mes = datetime.date.today().month
            ano = datetime.date.today().year
        else:
            mes = int(request.GET.get("mes", datetime.date.today().month))
            ano = int(request.GET.get("ano", datetime.date.today().year))
        mes_atual = datetime.date(year=ano, month=mes, day=1)
        mes_anterior = (mes_atual - datetime.timedelta(days=1)).replace(day=1)
        mes_proximo = mes_atual + datetime.timedelta(
            days=calendar.monthrange(mes_atual.year, mes_atual.month)[1]
        )

        return mes_atual, mes_anterior, mes_proximo

    def get_queryset(self, request):
        mes_atual, mes_anterior, mes_proximo = self.get_meses(request)
        return (
            super()
            .get_queryset(request)
            .filter(
                (
                    Q(data_ativacao__year=mes_atual.year)
                    & Q(Q(data_ativacao__month=mes_atual.month))
                )
                | (
                    Q(data_ativacao__year=mes_anterior.year)
                    & Q(Q(data_ativacao__month=mes_anterior.month))
                )
            )
            .values(
                servico=F("tipo_servico__nome"),
                mes=TruncMonth("data_ativacao"),
            )
            .annotate(ativados=Count("casa_legislativa__id", distinct=True))
        )

    def get_labels(self, request, queryset=None):
        mes_atual, mes_anterior, mes_proximo = self.get_meses(request)
        return [
            _("Total de casas atendidas"),
            _(f"Novas casas em {mes_anterior:%m/%Y}"),
            _(f"Novas casas em {mes_atual:%m/%Y}"),
        ]

    def get_datasets(self, request, queryset=None):
        mes_atual, mes_anterior, mes_proximo = self.get_meses(request)
        if queryset is None:
            queryset = self.get_queryset(request)
        labels = self.get_labels(request, queryset)
        datasets = {
            s["servico"]: {
                "total": s["total"],
                mes_anterior: 0,
                mes_atual: 0,
                "servico_id": s["servico_id"],
            }
            for s in Servico.objects.filter(data_desativacao=None)
            .values(
                servico=F("tipo_servico__nome"),
                servico_id=F("tipo_servico__id"),
            )
            .annotate(total=Count("casa_legislativa", distinct=True))
        }
        for data in queryset:
            datasets[data["servico"]][data["mes"]] = data["ativados"]

        return [
            {
                "label": label,
                "data": {
                    labels[0]: data["total"],
                    labels[1]: data[mes_atual],
                    labels[2]: data[mes_anterior],
                },
                "links": [
                    self.get_view_link(
                        "total", data["servico_id"], data["total"]
                    ),
                    self.get_view_link(
                        mes_atual, data["servico_id"], data[mes_atual]
                    ),
                    self.get_view_link(
                        mes_anterior, data["servico_id"], data[mes_anterior]
                    ),
                ],
            }
            for label, data in datasets.items()
        ]

    def get_view_link(self, x_axis, y_axis, value):
        if value == 0:
            return None
        base_url = reverse("admin:servicos_servico_changelist")
        qstrs = [
            "data_desativacao__isnull=True",
            f"tipo_servico__id__exact={y_axis}",
        ]
        if not isinstance(x_axis, str):
            qstrs.extend(
                [
                    f"data_ativacao__year={x_axis.year}",
                    f"data_ativacao__month={x_axis.month}",
                ]
            )
        qstrs = "&".join(qstrs)
        return f"{base_url}?{qstrs}"

    def get_prev_page(self, request=None, queryset=None):
        mes_atual, mes_anterior, mes_proximo = self.get_meses(request)
        params = QueryDict().copy()
        params["ano"] = mes_anterior.year
        params["mes"] = mes_anterior.month
        return params.urlencode()

    def get_next_page(self, request=None, queryset=None):
        mes_atual, mes_anterior, mes_proximo = self.get_meses(request)
        params = QueryDict().copy()
        params["ano"] = mes_proximo.year
        params["mes"] = mes_proximo.month
        return params.urlencode()


class AtualizacaoServicos(Dashcard):
    title = _("Frequência de atualização")
    chart_type = Dashcard.TYPE_BAR
    model = TipoServico

    intervalos = [
        ("Na semana", 7, "updated"),
        ("No mês", 30, "week"),
        ("No trimestre", 90, "month"),
        ("No semestre", 182, "quarter"),
        ("No ano", 365, "semester"),
        ("Mais de ano", 0, "year"),
        ("Erro na verificação", None, "err"),
    ]

    def get_queryset(self, request):
        counts = {}
        hoje = timezone.localdate()
        ate = hoje

        for label, dias, *__ in self.intervalos:
            if dias is None:
                counts[slugify(label)] = Count(
                    "servico", ~Q(servico__erro_atualizacao="")
                )
            elif dias > 0:
                de = hoje - datetime.timedelta(days=dias)
                counts[slugify(label)] = Count(
                    "servico", Q(servico__data_ultimo_uso__range=(de, ate))
                )
                ate = de - datetime.timedelta(days=1)
            else:
                counts[slugify(label)] = Count(
                    "servico", Q(servico__data_ultimo_uso__lte=ate)
                )

        return (
            super()
            .get_queryset(request)
            .exclude(string_pesquisa="")
            .filter(servico__data_desativacao=None)
            .annotate(**counts)
        )

    def get_labels(self, request, queryset=None):
        return [label for label, *__ in self.intervalos]

    def get_datasets(self, request, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)
        return [
            {
                "type": "bar",
                "label": ts.sigla,
                "data": {
                    label: getattr(ts, slugify(label))
                    for label, *__ in self.intervalos
                },
                "backgroundColor": getcolor(ts.sigla),
                "links": [
                    self.get_view_link(
                        ts.id, atualizacao, getattr(ts, slugify(label))
                    )
                    for label, dias, atualizacao in self.intervalos
                ],
            }
            for ts in queryset
        ]

    def get_view_link(self, x_axis, y_axis, value):
        print(x_axis, y_axis, value)
        base_url = reverse("admin:servicos_servico_changelist")
        return (
            f"{base_url}?data_desativacao__isnull=True"
            f"&atualizacao={y_axis}"
            f"&tipo_servico__id__exact={x_axis}"
        )


class UsoServicos(Dashcard):
    title = _("Uso dos serviços")
    chart_type = Dashcard.TYPE_BAR
    model = TipoServico
    filterset = UsoServicosFilter
    label_field = "sigla"

    def get_dataset_color(self, dataset_label):
        return getcolor(dataset_label)

    def apply_filters(self, request, queryset):
        queryset = queryset.exclude(string_pesquisa="").filter(
            servico__data_desativacao=None
        )
        return super().apply_filters(request, queryset)

    def get_datasets(self, request, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)

        counts = {
            f"{key}_count": Count(
                "servico",
                distinct=True,
                filter=Q(servico__resultado_verificacao=key),
            )
            for key, *__ in Servico.RESULTADO_CHOICES
        }

        queryset = queryset.annotate(**counts)

        return [
            {
                "label": label,
                "data": {r.sigla: getattr(r, f"{key}_count") for r in queryset},
                "links": [
                    self.get_view_link(r.id, key, getattr(r, f"{key}_count"))
                    for r in queryset
                ],
            }
            for key, label in Servico.RESULTADO_CHOICES
        ]

    def get_view_link(self, x_axis, y_axis, value):
        base_url = reverse("admin:servicos_servico_changelist")
        return (
            f"{base_url}?data_desativacao__isnull=True"
            f"&resultado_verificacao__exact={y_axis}"
            f"&tipo_servico__id__exact={x_axis}"
        )


class ServicosAno(Dashcard):
    title = _("Serviços hospedados por ano")
    chart_type = Dashcard.TYPE_BAR
    model = Servico
    filterset = AnoServicoFilter
    chart_options = {
        "scales": {"x": {"stacked": True}, "y": {"stacked": True}},
        "plugins": {"tooltip": {"mode": "index"}},
    }

    def get_dataset_color(self, dataset_label):
        return getcolor(dataset_label)

    def apply_filters(self, request, queryset):
        return (
            super()
            .apply_filters(request, queryset)
            .filter(hospedagem_interlegis=True)
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.GET.get("ano", None):
            # Usuário informou um ano, então vamos mostrar os meses daquele ano
            qs = (
                qs.order_by("data_ativacao__month", "tipo_servico__sigla")
                .values(
                    label=F("data_ativacao__month"),
                    sigla=F("tipo_servico__sigla"),
                )
                .annotate(total=Count("id"))
            )
        else:
            qs = (
                qs.order_by("data_ativacao__year", "tipo_servico__sigla")
                .values(
                    label=F("data_ativacao__year"),
                    sigla=F("tipo_servico__sigla"),
                )
                .annotate(total=Count("id"))
            )
        return qs

    def get_labels(self, request, queryset=None):
        if queryset is None:
            return list(
                Servico.objects.filter(hospedagem_interlegis=True)
                .order_by("data_ativacao__year")
                .values_list("data_ativacao__year")
                .distinct("data_ativacao__year")
            )

        if request.GET.get("ano", None):
            lang = to_locale(get_language()) + ".UTF-8"
            locale.setlocale(locale.LC_ALL, lang)
            map_function = lambda x: _(calendar.month_abbr[x])
        else:
            map_function = str

        labels = list({r["label"] for r in queryset})
        labels.sort()
        labels = list(map(map_function, labels))

        return labels

    def get_datasets(self, request, queryset=None):
        meses = {calendar.month_abbr[x + 1]: str(x + 1) for x in range(12)}
        ano = request.GET.get("ano", None)
        if queryset is None:
            queryset = self.get_queryset(request)
        if ano:
            lang = to_locale(get_language()) + ".UTF-8"
            locale.setlocale(locale.LC_ALL, lang)
            map_function = lambda x: _(calendar.month_abbr[x])
            map_yaxis = lambda x: {
                "data_ativacao__year": ano,
                "data_ativacao__month": meses[x],
            }
        else:
            map_function = str
            map_yaxis = lambda x: {"data_ativacao__year": x}

        labels = self.get_labels(request, queryset)

        series = {}
        for d in queryset:
            sigla = d["sigla"]
            label = map_function(d["label"])
            if sigla not in series:
                series[sigla] = dict(zip(labels, [0] * len(labels)))
            series[sigla][label] = d["total"]

        return [
            {
                "label": s,
                "data": series[s],
                "backgroundColor": getcolor(s),
                "links": [
                    self.get_view_link(s, map_yaxis(k), v)
                    for k, v in series[s].items()
                ],
            }
            for s in series
        ]

    def get_view_link(self, xaxis, yaxis, value):
        base_url = reverse("admin:servicos_servico_changelist")
        if value > 0:
            yaxis["hospedagem_interlegis__exact"] = 1
            try:
                yaxis["tipo_servico__id__exact"] = TipoServico.objects.get(
                    sigla=xaxis
                ).id
            except (
                TipoServico.DoesNotExist,
                TipoServico.MultipleObjectsReturned,
            ):
                return None
            return f"{base_url}?{urlencode(yaxis)}"
        return None
