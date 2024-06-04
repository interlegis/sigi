import csv
import docutils.core
import io
import re
from parsel import Selector
from contextlib import redirect_stdout, redirect_stderr
from django.apps import apps
from django.http.response import HttpResponse as HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib.admin.utils import label_for_field, get_fields_from_path
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import ListView
from django_extensions.management.jobs import get_job
from django_weasyprint import WeasyTemplateResponse
from django.utils.translation import gettext_lazy as _


class ReportListView(ListView):
    filter_form = None
    filter_form_initials = None
    template_name = None
    template_name_pdf = None
    pdf_suffix = "_pdf"
    format_param_name = "fmt"
    filename = None
    title = None
    list_fields = None
    list_labels = None
    link_fields = None
    change_field = None
    break_field = None
    empty_message = _("No data to display")

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_queryset(queryset)

    def get_template_names(self):
        snake_name = re.sub(
            r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__
        ).lower()
        app = apps.get_containing_app_config(self.__class__.__module__)
        app_label = "." if app is None else app.label
        if self._is_pdf():
            if self.template_name_pdf:
                return [self.template_name_pdf]
            if self.template_name:
                name = self.template_name[::-1].replace(
                    ".", f"{self.pdf_suffix}."[::-1], 1
                )[::-1]
                if self.pdf_suffix not in name:
                    name += self.pdf_suffix
                return [name]
            return [
                f"{app_label}/report/{snake_name}/report_pdf.html",
                f"{app_label}/report/report_pdf.html",
                "utils/report/report_pdf.html",
            ]
        else:
            if self.template_name is not None:
                return [self.template_name]
            else:
                return [
                    f"{app_label}/report/{snake_name}/report.html",
                    f"{app_label}/report/report.html",
                    "utils/report/report.html",
                ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report_title"] = self.get_title()
        context["list_labels"] = self.get_list_labels()
        context["list_fields"] = self.list_fields
        context["link_fields"] = self.link_fields
        context["change_field"] = self.change_field
        context["break_field"] = self.break_field
        context["empty_message"] = self.empty_message
        context["opts"] = self._get_options()
        context["form"] = self.get_filter_form_instance()
        return context

    def render_to_response(self, context, **response_kwargs):
        if self._is_csv():
            dataset, fieldnames = self.get_dataset(context)
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{self.get_filename()}.csv"'
            )
            writer = csv.DictWriter(response, fieldnames)
            writer.writeheader()
            writer.writerows(dataset)
            return response
        if self._is_pdf():
            self.response_class = WeasyTemplateResponse
            self.content_type = "application/pdf"
            response_kwargs["filename"] = f"{self.get_filename()}.pdf"
        return super().render_to_response(context, **response_kwargs)

    def filter_queryset(self, queryset):
        form = self.get_filter_form_instance()
        if form:
            if form.is_valid():
                filter = form.cleaned_data
            else:
                filter = self.filter_form_initials
            if filter:
                queryset = queryset.filter(**filter)
        return queryset

    def get_filter_form_instance(self):
        form = None
        if self.filter_form:
            form = self.filter_form(initial=self.filter_form_initials)
            if set(form.fields.keys()) & set(self.request.GET.keys()):
                form = self.filter_form(self.request.GET)
        return form

    def get_dataset(self, context):
        return (
            self.get_queryset().values(*self.list_fields),
            self.list_fields,
        )

    def get_filename(self):
        return self.filename or self.title or self.__class__.__name__

    def get_title(self):
        return self.title or ""

    def get_list_labels(self):
        if self.list_labels:
            return self.list_labels
        if not self.list_fields:
            raise ImproperlyConfigured(
                "ReportListView requires a list of field names to be "
                "displayed on report list data"
            )
        queryset = self.get_queryset()
        fields = [
            get_fields_from_path(queryset.model, path)[-1]
            for path in self.list_fields
        ]
        return [label_for_field(f.name, f.model) for f in fields]

    def _get_options(self):
        return self.get_queryset().model._meta

    def _is_pdf(self):
        return self.request.GET.get(self.format_param_name, "html") == "pdf"

    def _is_csv(self):
        return self.request.GET.get(self.format_param_name, "html") == "csv"


@login_required
@user_passes_test(lambda user: user.is_superuser)
def user_run_job(request, job_name):
    job = get_job(None, job_name)()
    start_time = timezone.localtime()
    if hasattr(job, "do_job"):
        job.do_job()
        end_time = timezone.localtime()
        rst, html = job.prepare_report(start_time, end_time)
    else:
        with io.StringIO() as so_buf, io.StringIO() as se_buf, redirect_stdout(
            so_buf
        ), redirect_stderr(se_buf):
            job.execute()
            messages = so_buf.getvalue()
            errors = se_buf.getvalue()
        report_data = ["", "MENSAGENS", "---------", ""]
        if messages:
            report_data.extend(messages.splitlines())
        else:
            report_data.extend(["Nenhuma mensagem gerada", ""])
        report_data.extend(["", "ERROS", "-----", ""])
        if errors:
            report_data.extend(errors.splitlines())
        else:
            report_data.extend(["Nenhum erro gerado", ""])
        end_time = timezone.localtime()
        rst = render_to_string(
            "emails/base_report.rst",
            {
                "title": job.help,
                "start_time": start_time,
                "end_time": end_time,
                "report_data": report_data,
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

    dp = Selector(text=html)

    return render(
        request,
        "admin/jobs/job_result.html",
        {"content": dp.xpath("//body/*").get()},
    )
