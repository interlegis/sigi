from django.contrib import admin
from django.contrib.admin.utils import build_q_object_from_lookup_parameters
from django.utils.translation import gettext as _
from sigi.apps.convenios.models import Projeto


class TipoProjetoFilter(admin.FieldListFilter):
    parameter_name = "convenio"

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(
            field, request, params, model, model_admin, field_path
        )

        self.lookup_choices = self.lookups(request, model_admin)
        if self.lookup_choices is None:
            self.lookup_choices = ()

    def lookups(self, request, model_admin):
        return (
            ("SC", _("Sem nenhum convênio")),
            ("CC", _("Com algum convênio")),
        ) + tuple([(p.pk, p.sigla) for p in Projeto.objects.all()])

    def value(self):
        return self.used_parameters.get(self.parameter_name)

    def expected_parameters(self):
        return [
            self.parameter_name,
        ]

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(
                remove=[self.parameter_name]
            ),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": str(self.value()) == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            if value[-1] == "SC":
                queryset = queryset.filter(**{self.field_path: None})
            elif value[-1] == "CC":
                queryset = queryset.exclude(**{self.field_path: None})
            else:
                queryset = queryset.filter(
                    build_q_object_from_lookup_parameters(
                        {self.field_path: value}
                    )
                )
        return queryset


class ExcluirTipoProjetoFilter(admin.FieldListFilter):
    parameter_name = "excluir_convenio"

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(
            field, request, params, model, model_admin, field_path
        )
        self.title = _(f"Excluir {self.title}")

        self.lookup_choices = self.lookups(request, model_admin)
        if self.lookup_choices is None:
            self.lookup_choices = ()

    def lookups(self, request, model_admin):
        return tuple([(p.pk, p.sigla) for p in Projeto.objects.all()])

    def value(self):
        return self.used_parameters.get(self.parameter_name)

    def expected_parameters(self):
        return [
            self.parameter_name,
        ]

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(
                remove=[self.parameter_name]
            ),
            "display": _("None"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": str(self.value()) == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            queryset = queryset.exclude(
                build_q_object_from_lookup_parameters({self.field_path: value})
            )
        return queryset
