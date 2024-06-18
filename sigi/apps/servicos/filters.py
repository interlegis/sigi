from datetime import date, timedelta
from django.utils.translation import gettext as _
from django.contrib import admin


class ServicoAtivoFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.model = model
        self.model_admin = model_admin
        self.parameter_name = f"{field_path}__isnull"
        super().__init__(
            field, request, params, model, model_admin, field_path
        )
        self.title = _("Serviço ativo")
        lookup_choices = self.lookups(request, model_admin)
        if lookup_choices is None:
            lookup_choices = ()
        self.lookup_choices = list(lookup_choices)

    def lookups(self, request, model_admin):
        return (("True", _("Ativo")), ("False", _("Inativo")))

    def has_output(self):
        return self.model.objects.exists()

    def value(self):
        return self.used_parameters.get(self.parameter_name)

    def expected_parameters(self):
        return [
            self.parameter_name,
        ]

    def choices(self, changelist):
        value = self.value()
        if isinstance(value, list):
            value = value[-1]
        yield {
            "selected": value is None,
            "query_string": changelist.get_query_string(
                remove=[self.parameter_name]
            ),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": str(value) == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }


class DataUtimoUsoFilter(admin.SimpleListFilter):
    title = _("Atualização")
    parameter_name = "atualizacao"

    def lookups(self, request, model_admin):
        return (
            ("err", _("Erro na verificação")),
            ("year", _("Sem atualização há um ano ou mais")),
            ("semester", _("Sem atualização de seis meses a um ano")),
            ("quarter", _("Sem atualização de três a seis meses")),
            ("month", _("Sem atualização de um a três meses")),
            ("week", _("Sem atualização de uma semana a um mês")),
            ("updated", _("Atualizado na última semana")),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            queryset = queryset.exclude(tipo_servico__string_pesquisa="")
            if self.value() == "err":
                return queryset.exclude(erro_atualizacao="")
            if self.value() == "year":
                limite = date.today() - timedelta(days=366)
                return queryset.filter(data_ultimo_uso__lte=limite)
            if self.value() == "updated":
                limite = date.today() - timedelta(days=7)
                return queryset.filter(data_ultimo_uso__gte=limite)
            if self.value() == "semester":
                de = date.today() - timedelta(days=365)
                ate = date.today() - timedelta(days=6 * 30 + 1)
            elif self.value() == "quarter":
                de = date.today() - timedelta(days=6 * 30)
                ate = date.today() - timedelta(days=3 * 30 + 1)
            elif self.value() == "month":
                de = date.today() - timedelta(days=3 * 30)
                ate = date.today() - timedelta(days=31)
            elif self.value() == "week":
                de = date.today() - timedelta(days=30)
                ate = date.today() - timedelta(days=7)
            return queryset.filter(data_ultimo_uso__range=(de, ate))
