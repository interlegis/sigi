from datetime import date, timedelta
from django.utils.translation import gettext as _
from django.contrib import admin

class ServicoAtivoFilter(admin.FieldListFilter):
    parameter_name = None

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.model = model
        self.model_admin = model_admin
        self.parameter_name = f'{field_path}__isnull'

        super().__init__(field, request, params, model, model_admin, field_path)

        self.title = _("Serviço ativo")

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value
        lookup_choices = self.lookups(request, model_admin)

        if lookup_choices is None:
            lookup_choices = ()
        self.lookup_choices = list(lookup_choices)

    def lookups(self, request, model_admin):
        return (
            ('True', _('Ativo')),
            ('False', _('Inativo'))
        )

    def has_output(self):
        return self.model.objects.exists()

    def value(self):
        return self.used_parameters.get(self.parameter_name)

    def expected_parameters(self):
        return [self.parameter_name,]

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(
                remove=[self.parameter_name]),
            'display': _('All'),
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': str(self.value()) == str(lookup),
                'query_string': changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                'display': title,
            }

class DataUtimoUsoFilter(admin.SimpleListFilter):
    title = _("Atualização")
    parameter_name = 'atualizacao'

    def lookups(self, request, model_admin):
        return (
            ('err', _("Erro na verificação")),
            ('year', _("Sem atualização há um ano ou mais")),
            ('semester', _("Sem atualização de seis meses a um ano")),
            ('quarter', _("Sem atualização de três a seis meses")),
            ('month', _("Sem atualização de um a três meses")),
            ('week', _("Sem atualização de uma semana a um mês")),
            ('updated', _("Atualizado na última semana")),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            queryset = queryset.exclude(tipo_servico__string_pesquisa="")
            if self.value() == 'err':
                queryset = queryset.exclude(erro_atualizacao="")
            elif self.value() == 'year':
                limite = date.today() - timedelta(days=365)
                queryset = queryset.filter(data_ultimo_uso__lte=limite)
            else:
                de = date.today() - (
                    timedelta(days=365) if self.value() == 'semester' else
                    timedelta(days=6*30) if self.value() == 'quarter' else
                    timedelta(days=3*30) if self.value() == 'month' else
                    timedelta(days=30) if self.value() == 'week' else
                    timedelta(days=0)
                )
                ate = date.today() - (
                    timedelta(days=6*30) if self.value() == 'semester' else
                    timedelta(days=3*30) if self.value() == 'quarter' else
                    timedelta(days=30) if self.value() == 'month' else
                    timedelta(days=7) if self.value() == 'week' else
                    timedelta(days=0)
                )
                queryset = queryset.filter(data_ultimo_uso__range=(de, ate))
        return queryset
