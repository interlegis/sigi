from collections import OrderedDict
from functools import update_wrapper
from django import forms
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.utils import pretty_name
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.http import Http404
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext as _, ngettext
from import_export import resources
from import_export.admin import ExportMixin
from import_export.forms import ExportForm
from import_export.signals import post_export
from sigi.apps.utils import field_label

class ExportFormFields(ExportForm):
   def __init__(self, formats, field_list, *args, **kwargs):
        super().__init__(formats, *args, **kwargs)
        self.fields['selected_fields'] = forms.MultipleChoiceField(
            label=_('Campos a exportar'),
            required=True,
            choices=field_list,
            initial=[f[0] for f in field_list],
            widget=forms.CheckboxSelectMultiple,
        )

class LabeledResourse(resources.ModelResource):
    selected_fields = None
    def get_export_headers(self):
        headers = []
        for field in self.get_export_fields():
            if field.attribute == field.column_name:
                label = field_label(field.attribute, self._meta.model)
            else:
                label = field.column_name
            headers.append(label)
        return headers

    def get_export_fields(self):
        fields = self.get_fields()
        if self.selected_fields:
            fields = [f for f in fields
                      if self.get_field_name(f) in self.selected_fields]
        return fields

    def export(self, queryset=None, selected_fields=None, *args, **kwargs):
        self.selected_fields = selected_fields
        return super().export(queryset, *args, **kwargs)

class CartExportMixin(ExportMixin):
    to_encoding = 'utf-8'
    change_list_template = 'admin/cart/change_list_cart_export.html'
    _cart_session_name = None
    _cart_viewing_name = None

    def __init__(self, *args, **kwargs):
        super(CartExportMixin, self).__init__(*args, **kwargs)
        self._cart_session_name = 'cart_%s' % self.opts.model_name
        self._cart_viewing_name = 'view_cart_%s' % self.opts.model_name

    def get_queryset(self, request):
        qs = super(CartExportMixin, self).get_queryset(request)
        if self._cart_viewing_name in request.session:
            ids = request.session.get(self._cart_session_name, [])
            qs = qs.filter(id__in=ids)
        return qs

    def get_actions(self, request):
        if self._cart_viewing_name in request.session:
            action = self.get_action('remove_from_cart')
            return OrderedDict([(action[1], action)])
        else:
            if self.actions is None:
                self.actions = []
            self.actions.append('add_to_cart')
            return super(CartExportMixin, self).get_actions(request)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if 'cart' in request.GET:
            request.GET._mutable = True
            cart = request.GET.get('cart', '0')
            request.GET.pop('cart', None)
            request.GET._mutable = False
            if cart == '1':
                request.session[self._cart_viewing_name] = True
            else:
                request.session.pop(self._cart_viewing_name, None)

        cart_item_count = len(request.session.get(self._cart_session_name, []))

        extra_context = extra_context or {}
        extra_context['cart_item_count'] = cart_item_count

        if self._cart_viewing_name in request.session:
            extra_context['viewing_cart'] = True
        return super(CartExportMixin, self).changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('clearcart/',
                self.admin_site.admin_view(self.clear_cart),
                name='%s_%s_clearcart' % self.get_model_info()),
        ]
        return my_urls + urls

    @csrf_protect_m
    def add_to_cart(self, request, queryset):
        if request.POST.get('select_across', '0') == '0':
            selected_ids = set(
                request.POST.getlist(helpers.ACTION_CHECKBOX_NAME, [])
            )
        else:
            selected_ids = set(
                map(str, queryset.values_list('id', flat=True))
            )

        if self._cart_session_name in request.session:
            cart_ids = set(request.session[self._cart_session_name])
        else:
            cart_ids = set()

        quant = len(selected_ids.difference(cart_ids))

        if quant:
            cart_ids.update(selected_ids)
            request.session[self._cart_session_name] = list(cart_ids)
            self.message_user(
                request,
                _(u"%s itens adicionados no carrinho") % quant)
        else:
            self.message_user(
                request,
                _(u"Os itens selecionados já estavam no carrinho"))
        return HttpResponseRedirect('.')
    add_to_cart.short_description = _(
        "Armazenar itens no carrinho para exportar"
    )

    @csrf_protect_m
    def remove_from_cart(self, request, queryset):
        if self._cart_session_name not in request.session:
            self.message_user(request, _(u"O carrinho está vazio"))
            return HttpResponseRedirect('.')

        if request.POST.get('select_across', '0') == '0':
            remove_ids = set(request.POST.getlist(helpers.ACTION_CHECKBOX_NAME))
        else:
            remove_ids = set(map(str, queryset.values_list('id', flat=True)))
        cart_ids = set(request.session[self._cart_session_name])

        request.session[self._cart_session_name] = list(
            cart_ids.difference(remove_ids)
        )

        self.message_user(request, _(u"%s itens removidos do carrinho.") %
                          len(cart_ids.intersection(remove_ids)))

        return HttpResponseRedirect('.')
    remove_from_cart.short_description = _("Remove itens do carrinho")

    @csrf_protect_m
    def clear_cart(self, request):
        request.session.pop(self._cart_session_name, None)
        request.session.pop(self._cart_viewing_name, None)
        self.message_user(request, _(u"Carrinho vazio"))
        return HttpResponseRedirect('..')

    @csrf_protect_m
    def export_action(self, request, *args, **kwargs):
        if not self.has_export_permission(request):
            raise PermissionDenied

        formats = self.get_export_formats()
        resource = (self.get_export_resource_class())()
        field_list = list(zip(resource.get_export_order(),
                              resource.get_export_headers()))
        form = ExportFormFields(formats, field_list, request.POST or None)
        if form.is_valid():
            file_format = formats[
                int(form.cleaned_data['file_format'])
            ]()

            queryset = self.get_export_queryset(request)
            export_data = self.get_export_data(
                file_format,
                queryset,
                request=request,
                encoding=self.to_encoding,
                selected_fields=form.cleaned_data['selected_fields'])
            content_type = file_format.get_content_type()
            response = HttpResponse(export_data, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (
                self.get_export_filename(request, queryset, file_format),
            )

            post_export.send(sender=None, model=self.model)
            return response

        context = self.get_export_context_data()

        context.update(self.admin_site.each_context(request))

        context['title'] = _("Export")
        context['form'] = form
        context['opts'] = self.model._meta
        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.export_template_name],
                                context)

class CartExportReportMixin(CartExportMixin):
    export_template_name = 'admin/import_export/export_report.html'
    reports = []

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('report/<str:name>/',
                self.admin_site.admin_view(self.report),
                name='%s_%s_report' % self.get_model_info()),
        ]
        return my_urls + urls

    def get_export_context_data(self):
        context = super().get_export_context_data()
        report_list = []
        for name in self.reports:
            report = getattr(self, name, None)
            if report is None:
                continue
            report_list.append(
                {'name': name,
                 'title': getattr(report, 'title', pretty_name(name)),
                 'icon': getattr(report, 'icon', 'picture_as_pdf')
                }
            )

        context['reports'] = report_list

        return context

    def report(self, request, name):
        if (name not in self.reports or not hasattr(self, name) or
            not callable(getattr(self, name))):
            raise Http404(_(f"Report {name} not exists"))

        report_view = getattr(self, name)

        return report_view(request)