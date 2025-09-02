from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django_weasyprint.views import WeasyTemplateResponse
from import_export.signals import post_export
from sigi.apps.utils import to_ascii


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


class AsciifyQParameter:
    def asciify_q_param(self, request):
        if "q" in request.GET:
            request.GET._mutable = True
            request.GET["q"] = to_ascii(request.GET["q"])
            request.GET._mutable = False

    def get_queryset(self, request):
        self.asciify_q_param(request)
        return super().get_queryset(request)


class StaffMemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ReportViewMixin:
    html_template_name = None
    pdf_template_name = None
    report_title = _("Report")
    pagesize = None
    attachment = True

    def _is_pdf(self):
        return bool(self.request.GET.get("pdf", 0))

    def get_template_names(self):
        if self.html_template_name is None or self.pdf_template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'html_template_name' and 'pdf_template_name' or an "
                "implementation of 'get_template_names()'"
            )
        if self._is_pdf():
            return [self.pdf_template_name]
        else:
            return [self.html_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.report_title
        context["pdf"] = self._is_pdf()
        if self.pagesize:
            context["pagesize"] = self.pagesize
        return context

    def render_to_response(self, context, **response_kwargs):
        self.response_class = TemplateResponse
        self.content_type = None
        if self._is_pdf():
            self.content_type = "application/pdf"
            self.response_class = WeasyTemplateResponse
            response_kwargs.setdefault(
                "filename",
                f"{self.report_title.lower()}-{timezone.localdate()}.pdf",
            )
            response_kwargs.setdefault("attachment", self.attachment)
        return super().render_to_response(context, **response_kwargs)
