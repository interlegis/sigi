from django.urls import reverse
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

    def get_view_link(self, x_axis, y_axis, value):
        try:
            s = Servidor.objects.exclude(casas_que_gerencia=None).get(
                nome_completo=x_axis
            )
        except:
            return None
        base_url = reverse("admin:casas_orgao_changelist")
        return f"{base_url}?gerentes_interlegis__id__exact={s.id}"


class PerformanceCarteira(Dashcard):
    chart_type = Dashcard.TYPE_DOUGHNUT
    title = _("Performance da gerência de carteiras")
    model = Orgao
    filterset = GerenteFilter

    LABEL_USAM = _("Utilizam serviços")
    LABEL_NAO_USAM = _("Não utilizam servços")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(gerentes_interlegis=None)

    def get_labels(self, request, queryset=None):
        return [self.LABEL_USAM, self.LABEL_NAO_USAM]

    def get_datasets(self, request, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)
        base_url = reverse("admin:casas_orgao_changelist")
        filter = self.get_filter(request.GET, queryset)
        filter.is_valid()
        servidor_id = filter.data.get("servidor")
        if servidor_id:
            servidor_qs = f"&gerentes_interlegis__id__exact={servidor_id}"
        else:
            servidor_qs = ""
        return [
            {
                "data": [
                    queryset.exclude(servico=None).count(),
                    queryset.filter(servico=None).count(),
                ],
                "links": [
                    f"{base_url}?tipo__legislativo__exact=1&servico=CS{servidor_qs}",
                    f"{base_url}?tipo__legislativo__exact=1&servico=SS{servidor_qs}",
                ],
            }
        ]
