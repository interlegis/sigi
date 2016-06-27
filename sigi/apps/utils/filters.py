# coding: utf-8
import string

from django.contrib import admin


class AlphabeticFilter(admin.SimpleListFilter):
        # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ''

    # Parameter for the filter that will be used in the URL query.
    parameter_name = ''

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ((letter, letter,) for letter in string.ascii_uppercase)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter((self.parameter_name + '__istartswith', self.value()))
