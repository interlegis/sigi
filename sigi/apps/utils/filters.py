import string
from math import log10
from django import forms
from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.utils import (
    build_q_object_from_lookup_parameters,
    prepare_lookup_value,
)
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext, gettext as _


def filter_single_value(value):
    if isinstance(value, list):
        return value[0]
    else:
        return value


class NotEmptyableField(Exception):
    pass


class AlphabeticFilter(admin.SimpleListFilter):
    title = ""
    parameter_name = None

    def lookups(self, request, model_admin):
        return (
            (
                letter,
                letter,
            )
            for letter in string.ascii_uppercase
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            queryset = queryset.filter(
                build_q_object_from_lookup_parameters(
                    {self.parameter_name + "__istartswith": self.value()}
                )
            )
        return queryset


class RangeFilter(admin.FieldListFilter):
    num_faixas = 4
    parameter_name = None

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.model = model
        self.model_admin = model_admin
        self.parameter_name = f"{field_path}__range"

        super().__init__(
            field, request, params, model, model_admin, field_path
        )

        lookup_choices = self.lookups(request, model_admin)

        if lookup_choices is None:
            lookup_choices = ()
        self.lookup_choices = list(lookup_choices)

    def ranges(self, model):
        tudo = model.objects.values_list(self.field_path, flat=True).order_by(
            self.field_path
        )
        passo = len(tudo) // self.num_faixas
        ultimo = 0

        for i in range(1, self.num_faixas):
            value = tudo[i * passo]
            if value > 100:
                if value > 1000:
                    log_val = int(log10(value))
                else:
                    log_val = int(log10(value)) - 1
                value = value // (10**log_val) * (10**log_val)
            yield (i, ultimo, value)
            ultimo = value

        yield (self.num_faixas, ultimo, tudo.last() + 1)

    def lookups(self, request, model_admin):
        def humanize(num):
            if num < 1000:
                return num
            log_val = int(log10(num))
            if log_val < 6:
                return ngettext(
                    f"{num//10**3} mil", f"{num//10**3} mil", num // 10**3
                )
            elif log_val < 9:
                return ngettext(
                    f"{num//10**6} milhão",
                    f"{num//10**6} milhões",
                    num // 10**6,
                )
            elif log_val < 12:
                return ngettext(
                    f"{num//10**9} bilhão",
                    f"{num//10**9} bilhões",
                    num // 10**9,
                )
            else:
                return ngettext(
                    f"{num//10**12} trilhão",
                    f"{num//10**12} trilhões",
                    num // 10**12,
                )

        primeiro, *meio, ultimo = self.ranges(self.model)
        value, min, max = primeiro
        yield (value, _(f"Até {humanize(max)}"))
        for value, min, max in meio:
            yield (value, _(f"de {humanize(min)} até {humanize(max)}"))
        value, min, max = ultimo
        yield (value, _(f"Acima de {humanize(min)}"))

    def has_output(self):
        return self.model.objects.exists()

    def value(self):
        value = self.used_parameters.get(self.parameter_name)
        if isinstance(value, list):
            return value[-1]
        return value

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
                "selected": str(lookup) == self.value(),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        try:
            for value, min, max in self.ranges(self.model):
                if str(value) == self.value():
                    return queryset.filter(
                        (f"{self.field_path}__gte", min),
                        (f"{self.field_path}__lt", max),
                    )
        except (ValueError, ValidationError) as e:
            raise IncorrectLookupParameters(e)

        return queryset


class DateRangeFilter(admin.FieldListFilter):
    template = "admin/date_range_filter.html"

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.model = model
        self.model_admin = model_admin
        self.lookup_kwargs = [f"{field_path}__gte", f"{field_path}__lte"]
        form_data = {}
        for p in self.expected_parameters():
            if p in params:
                value = params.pop(p)[-1]
                form_data[p] = prepare_lookup_value(
                    p, value, self.list_separator
                )
        super().__init__(
            field, request, params, model, model_admin, field_path
        )
        form = self.get_date_form(form_data)
        if form.is_valid():
            self.used_parameters = {
                key: [value]
                for key, value in form.cleaned_data.items()
                if value is not None
            }
        else:
            self.used_parameters = {}

    def has_output(self):
        return self.model.objects.exists()

    def expected_parameters(self):
        return self.lookup_kwargs

    def choices(self, changelist):
        form_params = {
            key: value[-1] for key, value in self.used_parameters.items()
        }
        return [
            {
                "query_string": changelist.get_query_string(
                    remove=self.lookup_kwargs
                ),
                "form": self.get_date_form(form_params, changelist),
            }
        ]

    def get_date_form(self, context={}, changelist=None):
        date_fields = {
            name: forms.DateField(
                required=False,
                label=(_("De") if "__gte" in name else _("Até")),
                widget=forms.DateInput(
                    attrs={
                        "class": "datepicker admin_filter",
                        "placeholder": (
                            _("De") if "__gte" in name else _("Até")
                        ),
                        "data-clear": (
                            changelist.get_query_string(
                                remove=[
                                    name,
                                ]
                            )
                            if changelist
                            else ""
                        ),
                    }
                ),
            )
            for name in self.lookup_kwargs
        }
        DateForm = type("DateForm", (forms.Form,), date_fields)

        return DateForm(context)
