import django_filters
from dashboard import Dashcard, getcolor
from django.db.models import Count
from django.utils.translation import gettext as _
from sigi.apps.casas.models import Orgao
from sigi.apps.servidores.models import Servidor


class GerenteFilter(django_filters.FilterSet):
    servidor = django_filters.ModelChoiceFilter(
        field_name="gerentes_interlegis",
        label="Gerente",
        queryset=Servidor.objects.exclude(casas_que_gerencia=None),
    )

    class Meta:
        model = Orgao
        fields = ["servidor"]


class CasasGerente(Dashcard):
    chart_type = Dashcard.TYPE_DOUGHNUT
    title = _("Distribuição de Casas por Gerente")
    model = Servidor
    label_field = "nome_completo"
    datasets = [{"data_field": ("casas_que_gerencia", Count)}]

    def apply_filters(self, request, queryset):
        return (
            super()
            .apply_filters(request, queryset)
            .exclude(casas_que_gerencia=None)
        )


class PerformanceCarteira(Dashcard):
    chart_type = Dashcard.TYPE_DOUGHNUT
    title = _("Performance da gerência de carteiras")
    model = Orgao
    filterset = GerenteFilter

    LABEL_USAM = _("Utilizam serviços")
    LABEL_NAO_USAM = _("Não utilizam servços")

    def apply_filters(self, request, queryset):
        filter = self.filterset(request.GET, queryset=queryset)
        valid = filter.is_valid()
        if filter.form.cleaned_data["servidor"] is None:
            if (
                request.user.servidor
                and request.user.servidor.casas_que_gerencia.exists()
            ):
                return request.user.servidor.casas_que_gerencia.all()
        return (
            super()
            .apply_filters(request, queryset)
            .exclude(gerentes_interlegis=None)
        )

    def get_labels(self, request, queryset=None):
        return [self.LABEL_USAM, self.LABEL_NAO_USAM]

    def get_datasets(self, request, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)
        return [
            {
                "data": [
                    queryset.exclude(servico=None).count(),
                    queryset.filter(servico=None).count(),
                ]
            }
        ]
