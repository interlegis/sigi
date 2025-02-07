import numpy as np
import pandas as pd
import django_filters
from dashboard import Dashcard
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.translation import gettext as _
from sigi.apps.casas.models import TipoOrgao, Orgao
from sigi.apps.convenios.models import Convenio, Projeto


def get_tipos():
    tipos = list(
        TipoOrgao.objects.filter(sigla__in=["CM", "AL"]).values_list(
            "sigla", "nome"
        )
    )
    tipos.extend(
        [
            ("_legislativo", _("Todo o legislativo")),
            ("_outros", _("Demais órgãos")),
        ]
    )
    return tipos


class ResumoConveniosFilter(django_filters.FilterSet):
    tipo = django_filters.ChoiceFilter(
        field_name="casa_legislativa__tipo__sigla",
        label=_("Tipo"),
        choices=get_tipos,
        method="filter_tipo",
        empty_label=None,
        initial="CM",
    )

    class Meta:
        model = Convenio
        fields = ["tipo"]

    def filter_tipo(self, queryset, name, value):
        if value == "_legislativo":
            tipos = TipoOrgao.objects.filter(legislativo=True).values_list(
                "sigla", flat=True
            )
        elif value == "_outros":
            tipos = TipoOrgao.objects.filter(legislativo=False).values_list(
                "sigla", flat=True
            )
        else:
            tipos = [value]
        return queryset.filter(**{f"{name}__in": tipos})


class ResumoConvenios(Dashcard):
    chart_type = Dashcard.TYPE_TABLE
    title = _("Resumo de informações")
    model = Convenio
    filterset = ResumoConveniosFilter
    template_table = "convenios/dashboard/resumo_convenios.html"

    def apply_filters(self, request, queryset):
        if "tipo" not in request.GET:
            request.GET = request.GET.copy()
            request.GET["tipo"] = "CM"
        return super().apply_filters(request, queryset)

    def get_labels(self, request, queryset=None):
        return []

    def get_datasets(self, request, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)
        filter = self.get_filter(request.GET, queryset)
        if filter and filter.is_valid():
            label_tipo = dict(get_tipos())[filter.form.cleaned_data["tipo"]]
        else:
            label_tipo = dict(get_tipos())["CM"]
        convenios = queryset
        camaras = filter.filter_tipo(
            Orgao.objects.all(),
            "tipo__sigla",
            filter.form.cleaned_data["tipo"],
        )
        convenios_vigentes = convenios.exclude(
            data_retorno_assinatura=None
        ).filter(
            Q(data_termino_vigencia__gte=timezone.localdate())
            | Q(data_termino_vigencia=None)
        )
        convenios_andando = convenios.filter(data_retorno_assinatura=None)
        convenios_vencidos = convenios.exclude(
            Q(data_retorno_assinatura=None) | Q(data_termino_vigencia=None)
        ).filter(data_termino_vigencia__lt=timezone.localdate())
        dataset = {
            _(f"{label_tipo} com convênios vigentes"): {
                k: v
                for k, v in convenios_vigentes.values_list(
                    "projeto__sigla"
                ).annotate(Count("casa_legislativa_id", distinct=True))
            },
            _(f"{label_tipo} com convênios em andamento"): {
                k: v
                for k, v in convenios_andando.values_list(
                    "projeto__sigla"
                ).annotate(Count("casa_legislativa_id", distinct=True))
            },
            _(f"{label_tipo} com convênios vencidos"): {
                k: v
                for k, v in convenios_vencidos.values_list(
                    "projeto__sigla"
                ).annotate(Count("casa_legislativa_id", distinct=True))
            },
        }

        ds_totais = (
            (_(f"Total de {label_tipo} do país"), camaras.count()),
            (
                _(f"Total de {label_tipo} com convênio vigente"),
                convenios_vigentes.order_by("casa_legislativa_id")
                .distinct("casa_legislativa_id")
                .count(),
            ),
            (
                _(f"Total de {label_tipo} com convênio em andamento"),
                convenios_andando.order_by("casa_legislativa_id")
                .distinct("casa_legislativa_id")
                .count(),
            ),
            (
                _(f"Total de {label_tipo} com convênio vencido"),
                convenios_vencidos.order_by("casa_legislativa_id")
                .distinct("casa_legislativa_id")
                .count(),
            ),
        )

        df = (
            pd.DataFrame.from_dict(dataset, orient="index")
            .replace(np.nan, 0)
            .convert_dtypes()
        )

        return {"data_frame": df, "totais": ds_totais}


class ConvenioServico(Dashcard):
    chart_type = Dashcard.TYPE_TABLE
    title = _("Convenios e serviços")
    model = Orgao
    label_name = _("Situação")

    def get_queryset(self, request):
        return (
            Orgao.objects.exclude(servico=None)
            .filter(servico__data_desativacao=None, convenio=None)
            .aggregate(
                total=Count("id", distinct=True),
                hospedagem=Count(
                    "id",
                    filter=Q(servico__tipo_servico__modo="H"),
                    distinct=True,
                ),
            )
        )

    def get_labels(self, request, queryset=None):
        return [_("Total")]

    def get_datasets(self, request, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)
        values = dict(queryset)
        datasets = [
            {
                "label": _(
                    "Casas sem convenio que utilizam algum serviço de hospedagem"
                ),
                "data": [values["hospedagem"]],
            },
            {
                "label": _(
                    "Casas sem convenio que utilizam somente serviço de registro"
                ),
                "data": [values["total"] - values["hospedagem"]],
            },
            {
                "label": _(
                    "Casas sem convenio que utilizam algum serviço de registro e/ou hospedagem"
                ),
                "data": [values["total"]],
            },
        ]
        return datasets
