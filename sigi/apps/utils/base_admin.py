from django.contrib import admin
from django.contrib.admin.views.main import ChangeList


class ClearAllFilter(object):
    title = None
    template = "clear_all_filter.html"

    def __init__(self, disabled):
        self.disabled = disabled

    def choices(self, cl):
        return [self.disabled]

    def queryset(self, request, queryset):
        return queryset


class BaseChangeList(ChangeList):
    def get_filters(self, request):
        (filter_specs, has_filters, lookup_params, use_distinct) = super(
            BaseChangeList, self
        ).get_filters(request)
        if filter_specs:
            clear_all_disabled = not self.get_filters_params()
            filter_specs = [ClearAllFilter(clear_all_disabled)] + filter_specs

        return (filter_specs, has_filters, lookup_params, use_distinct)


class BaseModelAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        return BaseChangeList
