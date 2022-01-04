# coding: utf-8
from django.contrib import admin
from django.utils.translation import gettext as _


class PopulationFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('População')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'faixa'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', _('< 100 Mil')),
            ('2', _('100 Mil a 1 Milhão')),
            ('3', _('1 Milhão a 100 Milhões')),
            ('4', _('> 100 Milhões')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '1', '2', '3' or '4')
        # to decide how to filter the queryset.
        if self.value() == '1':
            return queryset.filter(populacao__lt=100000)
        elif self.value() == '2':
            return queryset.filter(populacao__gte=100000, populacao__lt=1000000)
        elif self.value() == '3':
            return queryset.filter(populacao__gte=1000000, populacao__lt=10000000)
        elif self.value() == '4':
            return queryset.filter(populacao__gt=100000000)
        else:
            return queryset
