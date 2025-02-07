import calendar
import datetime
import django_filters
from dashboard import Dashcard, getcolor
from django.db.models import F, Count, Q
from django.utils import timezone
from django.utils.translation import gettext as _
from sigi.apps.eventos.models import Evento, TipoEvento


def get_anos():
    return [
        (str(a), str(a))
        for a in Evento.objects.filter(status=Evento.STATUS_REALIZADO)
        .order_by("data_inicio__year")
        .values_list("data_inicio__year", flat=True)
        .distinct("data_inicio__year")
    ]


class AnoFilterset(django_filters.FilterSet):
    ano = django_filters.ChoiceFilter(
        field_name="data_inicio",
        lookup_expr="year",
        label=_("Ano"),
        distinct=True,
        choices=get_anos,
    )

    class Meta:
        model = Evento
        fields = ["ano"]


class EventosStatus(Dashcard):
    chart_type = Dashcard.TYPE_DOUGHNUT
    title = _("Eventos por status")
    model = Evento
    label_field = ("status", F, lambda s: dict(Evento.STATUS_CHOICES)[s])
    datasets = [{"data_field": ("id", Count)}]

    def get_dataset_color(self, dataset_label):
        return getcolor(dataset_label)


class EventosAno(Dashcard):
    chart_type = Dashcard.TYPE_LINE
    title = _("Eventos nos últimos 12 meses")
    model = TipoEvento

    def get_dataset_color(self, dataset_label):
        print(f"EventosAno: {dataset_label}, {getcolor(dataset_label)}")
        return getcolor(dataset_label)

    def get_meses(self, request=None):
        if request is None:
            mes = timezone.localdate().month
            ano = timezone.localdate().year
        else:
            mes = int(request.GET.get("mes", timezone.localdate().month))
            ano = int(request.GET.get("ano", timezone.localdate().year))

        mes_ano = datetime.date(
            year=ano, month=mes, day=1
        ) + datetime.timedelta(days=calendar.monthrange(ano, mes)[1])

        meses = []

        for i in range(13):
            meses.append(mes_ano)
            mes_ano = (mes_ano - datetime.timedelta(days=1)).replace(day=1)
        meses.reverse()

        return meses

    def get_labels(self, request, queryset=None):
        return [f"{m:%m/%Y}" for m in self.get_meses(request)[:-1]]

    def get_counters(self, request):
        counts = {}
        for mes in self.get_meses(request)[:-1]:
            counts[f"count_{mes:%Y_%m}"] = Count(
                "evento",
                Q(
                    evento__data_inicio__year=mes.year,
                    evento__data_inicio__month=mes.month,
                ),
            )
        return counts

    def apply_filters(self, request, queryset):
        return (
            super()
            .apply_filters(request, queryset)
            .filter(evento__status=Evento.STATUS_REALIZADO)
        )

    def get_queryset(self, request):
        counts = self.get_counters(request)
        return (
            super()
            .get_queryset(request)
            .values("categoria")
            .annotate(**counts)
        )

    def get_dataset_color(self, dataset_label):
        return getcolor(dataset_label)

    def get_datasets(self, request, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)
        categorias = dict(TipoEvento.CATEGORIA_CHOICES)
        counters = self.get_counters(request).keys()
        return [
            {
                "label": categorias[r["categoria"]],
                "data": [r[c] for c in counters],
                "backgroundColor": self.get_dataset_color(r["categoria"]),
            }
            for r in queryset
        ]

    def get_next_page(self, request=None, queryset=None):
        mes = self.get_meses(request)[-1]
        return f"ano={mes.year}&mes={mes.month}"

    def get_prev_page(self, request=None, queryset=None):
        mes = self.get_meses(request)[-3]
        return f"ano={mes.year}&mes={mes.month}"


class EventosCategoria(Dashcard):
    chart_type = Dashcard.TYPE_DOUGHNUT
    title = _("Eventos por categoria")
    filterset = AnoFilterset
    model = Evento
    label_field = (
        "tipo_evento__categoria",
        F,
        lambda x: dict(TipoEvento.CATEGORIA_CHOICES)[x],
    )
    datasets = [{"data_field": ("id", Count)}]

    def apply_filters(self, request, queryset):
        return (
            super()
            .apply_filters(request, queryset)
            .filter(status=Evento.STATUS_REALIZADO)
        )

    def get_dataset_color(self, dataset_label):
        return getcolor(dataset_label)
