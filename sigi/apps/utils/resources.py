from import_export.fields import Field
from import_export.resources import ModelResource


class ValueField(Field):
    def get_value(self, obj):
        if self.attribute is None:
            return None
        return obj[self.attribute]


class ValueModelResource(ModelResource):
    DEFAULT_RESOURCE_FIELD = ValueField

    def filter_export(self, queryset, **kwargs):
        queryset = super().filter_export(queryset, **kwargs)
        selected_fields = kwargs.get("selected_fields", self.fields)
        return queryset.values(*selected_fields)
