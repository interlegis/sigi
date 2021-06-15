# coding: utf-8
import string
from django.utils.translation import gettext as _
from django.contrib import admin
from django.contrib.admin.utils import reverse_field_path

class RangeFieldListFilter(admin.FieldListFilter):
    slices = 5
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_gte = '%s__gte' % field_path
        self.lookup_kwarg_lt = '%s__lt' % field_path
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        self.lookup_val_gte = params.get(self.lookup_kwarg_gte)
        self.lookup_val_lt = params.get(self.lookup_kwarg_lt)
        self.lookup_val_isnull = params.get(self.lookup_kwarg_isnull)
        self.empty_value_display = model_admin.get_empty_value_display()
        parent_model, reverse_path = reverse_field_path(model, field_path)
        # Obey parent ModelAdmin queryset when deciding which options to show
        if model == parent_model:
            queryset = model_admin.get_queryset(request)
        else:
            queryset = parent_model._default_manager.all()
        self.lookup_choices = self.slice_range(queryset.order_by(field.name)
                                          .values_list(field.name, flat=True))
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lt,
                self.lookup_kwarg_isnull]

    def choices(self, changelist):
        yield {
            'selected': (self.lookup_val_gte is None and
                         self.lookup_val_lt is None and
                         self.lookup_val_isnull is None),
            'query_string': changelist.get_query_string(remove=[
                self.lookup_kwarg_gte, self.lookup_kwarg_lt,
                self.lookup_kwarg_isnull]),
            'display': _('All'),
        }
        last_val = None
        for val in self.lookup_choices:
            val = str(val)
            if last_val is None:
                last_val = val
                yield {
                    'selected': self.lookup_val_lt == val,
                    'query_string': changelist.get_query_string(
                        {self.lookup_kwarg_lt: val},
                        [self.lookup_kwarg_isnull, self.lookup_kwarg_gte]),
                    'display': _('Menor que %s') % val,
                }
            else:
                yield {
                    'selected': (self.lookup_val_gte == last_val and
                                 self.lookup_val_lt == val),
                    'query_string': changelist.get_query_string(
                        {self.lookup_kwarg_gte: last_val,
                         self.lookup_kwarg_lt: val},
                        [self.lookup_kwarg_isnull]),
                    'display': _("De %s até %s") % (last_val, val),
                }
                last_val = val

        yield {
            'selected': self.lookup_val_gte == last_val,
            'query_string': changelist.get_query_string(
                {self.lookup_kwarg_gte: last_val},
                [self.lookup_kwarg_isnull, self.lookup_kwarg_lt]),
            'display': _("De %s acima") % last_val,
        }

    def slice_range(self, queryset):
        if queryset.distinct().count() < self.slices:
            return list(queryset.distinct())

        total = queryset.count()
        salt = total // self.slices
        result = []

        for pos in range(salt, salt*self.slices, salt):
            result.append(queryset[pos])

        return result

class MultiRelatedFieldListFilter(admin.RelatedFieldListFilter):
    template = "admin/multifilter.html"
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.lookup_kwarg = '%s__%s__in' % (field_path, field.target_field.name)
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        self.lookup_val = params.get(self.lookup_kwarg)

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'query_string': changelist.get_query_string(
                remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            'display': _('All'),
        }
        for pk_val, val in self.lookup_choices:
            values = (set(self.lookup_val.split(',')) if self.lookup_val
                      else set())
            selected = str(pk_val) in values
            if selected:
                values.discard(str(pk_val))
            else:
                values.add(str(pk_val))

            if values:
                yield {
                    'selected': selected,
                    'query_string': changelist.get_query_string(
                        {self.lookup_kwarg: ",".join(values)},
                        [self.lookup_kwarg_isnull]),
                    'display': val,
                }
            else:
                yield {
                    'selected': selected,
                    'query_string': changelist.get_query_string(
                        remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]),
                    'display': val,
                }

        if self.include_empty_choice:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string(
                    {self.lookup_kwarg_isnull: 'True'}, [self.lookup_kwarg]
                ),
                'display': self.empty_value_display,
            }

class MultiChoicesFieldListFilter(admin.ChoicesFieldListFilter):
    template = "admin/multifilter.html"
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.lookup_kwarg = '%s__in' % field_path
        self.lookup_val = params.get(self.lookup_kwarg)

    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None,
            'query_string': changelist.get_query_string(
                remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            'display': _('All')
        }
        none_title = ''
        for lookup, title in self.field.flatchoices:
            values = (set(self.lookup_val.split(',')) if self.lookup_val
                      else set())
            selected = str(lookup) in values
            if selected:
                values.discard(str(lookup))
            else:
                values.add(str(lookup))

            if lookup is None:
                none_title = title
                continue

            if values:
                yield {
                    'selected': selected,
                    'query_string': changelist.get_query_string(
                        {self.lookup_kwarg: ",".join(values)},
                        [self.lookup_kwarg_isnull]),
                    'display': title,
                }
            else:
                yield {
                    'selected': selected,
                    'query_string': changelist.get_query_string(
                        remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]),
                    'display': title,
                }

        if none_title:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string(
                    {self.lookup_kwarg_isnull: 'True'}, [self.lookup_kwarg]
                ),
                'display': none_title,
            }