import datetime
import docutils.core
import traceback
from collections import OrderedDict
from functools import update_wrapper
from django import forms
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.utils import pretty_name
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.mail import mail_admins
from django.http import Http404
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext as _, ngettext
from import_export import resources
from import_export.admin import ImportMixin, ExportMixin
from import_export.fields import Field
from import_export.forms import ExportForm
from import_export.signals import post_export
from sigi.apps.utils import field_label


class MisconfiguredError(Exception):
    pass


class ValueField(Field):
    def get_value(self, obj):
        if self.attribute is None:
            return None
        return obj[self.attribute]


class ExportFormFields(ExportForm):
    def __init__(self, formats, resource_classes, *args, **kwargs):
        super().__init__(formats, resource_classes, *args, **kwargs)
        for i, resource_klass in enumerate(resource_classes):
            resource = resource_klass()
            field_list = list(
                zip(resource.get_export_order(), resource.get_export_headers())
            )
            self.fields[f"selected_fields_{i}"] = forms.MultipleChoiceField(
                label=_("Campos a exportar"),
                required=False,
                choices=field_list,
                initial=[f[0] for f in field_list],
                widget=forms.CheckboxSelectMultiple,
            )

    class Media:
        js = ("js/exportformfields.js",)


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
            fields = [
                f
                for f in fields
                if self.get_field_name(f) in self.selected_fields
            ]
        return fields

    def export(self, queryset=None, selected_fields=None, *args, **kwargs):
        self.selected_fields = selected_fields
        return super().export(queryset, *args, **kwargs)


class ValueLabeledResource(LabeledResourse):
    DEFAULT_RESOURCE_FIELD = ValueField

    def export(self, queryset=None, selected_fields=None, *args, **kwargs):
        queryset = queryset.values(*selected_fields)
        return super().export(queryset, selected_fields, *args, **kwargs)


class CartExportMixin(ExportMixin):
    to_encoding = "utf-8"
    import_export_change_list_template = (
        "admin/cart/change_list_cart_export.html"
    )
    export_form_class = ExportFormFields
    _cart_session_name = None
    _cart_viewing_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cart_session_name = "cart_%s" % self.opts.model_name
        self._cart_viewing_name = "view_cart_%s" % self.opts.model_name

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self._cart_viewing_name in request.session:
            ids = request.session.get(self._cart_session_name, [])
            qs = qs.filter(id__in=ids)
        return qs

    def get_actions(self, request):
        if self._cart_viewing_name in request.session:
            action = self.get_action("remove_from_cart")
            return OrderedDict([(action[1], action)])
        else:
            if self.actions is None:
                self.actions = []
            else:
                self.actions = list(self.actions)
            self.actions.append("add_to_cart")
            return super().get_actions(request)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if "cart" in request.GET:
            request.GET._mutable = True
            cart = request.GET.get("cart", "0")
            request.GET.pop("cart", None)
            request.GET._mutable = False
            if cart == "1":
                request.session[self._cart_viewing_name] = True
            else:
                request.session.pop(self._cart_viewing_name, None)

        cart_item_count = len(request.session.get(self._cart_session_name, []))

        extra_context = extra_context or {}
        extra_context["cart_item_count"] = cart_item_count

        if self._cart_viewing_name in request.session:
            extra_context["viewing_cart"] = True
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "clearcart/",
                self.admin_site.admin_view(self.clear_cart),
                name="%s_%s_clearcart" % self.get_model_info(),
            ),
        ]
        return my_urls + urls

    def get_data_for_export(self, request, queryset, *args, **kwargs):
        export_form = kwargs.get("export_form", None)
        resource_index = self.get_resource_index(export_form)
        field_name = f"selected_fields_{resource_index}"
        kwargs["selected_fields"] = export_form.cleaned_data[field_name]
        return super().get_data_for_export(request, queryset, *args, **kwargs)

    @csrf_protect_m
    def add_to_cart(self, request, queryset):
        if request.POST.get("select_across", "0") == "0":
            selected_ids = set(
                request.POST.getlist(helpers.ACTION_CHECKBOX_NAME, [])
            )
        else:
            selected_ids = set(map(str, queryset.values_list("id", flat=True)))

        if self._cart_session_name in request.session:
            cart_ids = set(request.session[self._cart_session_name])
        else:
            cart_ids = set()

        quant = len(selected_ids.difference(cart_ids))

        if quant:
            cart_ids.update(selected_ids)
            request.session[self._cart_session_name] = list(cart_ids)
            self.message_user(
                request, _("%s itens adicionados no carrinho") % quant
            )
        else:
            self.message_user(
                request, _("Os itens selecionados já estavam no carrinho")
            )
        return HttpResponseRedirect(".")

    add_to_cart.short_description = _(
        "Armazenar itens no carrinho para exportar"
    )

    @csrf_protect_m
    def remove_from_cart(self, request, queryset):
        if self._cart_session_name not in request.session:
            self.message_user(request, _("O carrinho está vazio"))
            return HttpResponseRedirect(".")

        if request.POST.get("select_across", "0") == "0":
            remove_ids = set(request.POST.getlist(helpers.ACTION_CHECKBOX_NAME))
        else:
            remove_ids = set(map(str, queryset.values_list("id", flat=True)))
        cart_ids = set(request.session[self._cart_session_name])

        request.session[self._cart_session_name] = list(
            cart_ids.difference(remove_ids)
        )

        self.message_user(
            request,
            _("%s itens removidos do carrinho.")
            % len(cart_ids.intersection(remove_ids)),
        )

        return HttpResponseRedirect(".")

    remove_from_cart.short_description = _("Remove itens do carrinho")

    @csrf_protect_m
    def clear_cart(self, request):
        request.session.pop(self._cart_session_name, None)
        request.session.pop(self._cart_viewing_name, None)
        self.message_user(request, _("Carrinho vazio"))
        return HttpResponseRedirect("..")


class CartImportExportMixin(ImportMixin, CartExportMixin):
    """
    Import and export mixin.
    """

    #: template for change_list view
    import_export_change_list_template = (
        "admin/cart/change_list_import_cart_export.html"
    )


class CartExportReportMixin(CartExportMixin):
    export_template_name = "admin/import_export/export_report.html"
    reports = []

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "report/<str:name>/",
                self.admin_site.admin_view(self.report),
                name="%s_%s_report" % self.get_model_info(),
            ),
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
                {
                    "name": name,
                    "title": getattr(report, "title", pretty_name(name)),
                    "icon": getattr(report, "icon", "picture_as_pdf"),
                }
            )

        context["reports"] = report_list

        return context

    def report(self, request, name):
        if (
            name not in self.reports
            or not hasattr(self, name)
            or not callable(getattr(self, name))
        ):
            raise Http404(_(f"Report {name} not exists"))

        report_view = getattr(self, name)

        return report_view(request)


class ReturnMixin:
    _return_path = None

    def changeform_view(
        self, request, object_id=None, form_url="", extra_context=None
    ):
        if "_return" in request.GET:
            self._return_path = request.GET.get("_return")
        return super().changeform_view(
            request, object_id, form_url, extra_context
        )

    def response_post_save_add(self, request, obj):
        if self._return_path:
            return HttpResponseRedirect(self._return_path)
        return super().response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        if self._return_path:
            return HttpResponseRedirect(self._return_path)
        return super().response_post_save_change(request, obj)

    def response_delete(self, request, obj_display, obj_id):
        response = super().response_delete(request, obj_display, obj_id)
        if self._return_path:
            return HttpResponseRedirect(self._return_path)
        return response


class JobReportMixin:
    error_report_template = "emails/report_error.rst"
    report_template = "emails/base_report.rst"
    report_data = None
    sys_user = None

    def execute(self):
        start_time = datetime.datetime.now()

        try:
            from sigi.apps.servidores.models import Servidor

            self.sys_user = Servidor.objects.get(sigi=True).user
        except Exception:
            pass

        try:
            self.do_job()
        except Exception as e:
            self.report_error(e)
            return
        end_time = datetime.datetime.now()
        self.report(start_time, end_time)

    def do_job(self):
        raise NotImplementedError("Job needs to implement the 'do_job' method")

    def _admin_log(self, object, action_flag, message=""):
        if self.sys_user is None:
            return  # No admin log
        LogEntry.objects.log_action(
            user_id=self.sys_user.id,
            content_type_id=ContentType.objects.get_for_model(type(object)).pk,
            object_id=object.id,
            object_repr=str(object),
            action_flag=action_flag,
            change_message=message,
        )

    def admin_log_addition(self, object, message=""):
        self._admin_log(object, ADDITION, message)

    def admin_log_change(self, object, message=""):
        self._admin_log(object, CHANGE, message)

    def report_error(self, error):
        rst = render_to_string(
            self.error_report_template,
            {
                "title": self.help,
                "traceback": traceback.format_exception(error),
            },
        )
        html = docutils.core.publish_string(
            rst,
            writer_name="html5",
            settings_overrides={
                "input_encoding": "unicode",
                "output_encoding": "unicode",
            },
        )
        mail_admins(
            subject=self.help,
            message=rst,
            html_message=html,
            fail_silently=True,
        )
        print(rst)

    def report(self, start_time, end_time):
        if self.report_data is None:
            raise MisconfiguredError(
                "Job needs to define 'report_data' property"
            )

        rst = render_to_string(
            self.report_template,
            {
                "title": self.help,
                "start_time": start_time,
                "end_time": end_time,
                "report_data": self.report_data,
            },
        )
        html = docutils.core.publish_string(
            rst,
            writer_name="html5",
            settings_overrides={
                "input_encoding": "unicode",
                "output_encoding": "unicode",
            },
        )
        mail_admins(
            subject=f"JOB: {self.help}",
            message=rst,
            html_message=html,
            fail_silently=True,
        )
        print(rst)
