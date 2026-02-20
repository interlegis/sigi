from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, path
from django.utils import timezone
from django.utils.formats import localize
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_extensions.management.jobs import get_job, get_jobs
from tinymce.models import HTMLField
from tinymce.widgets import AdminTinyMCE
from sigi.apps.utils.models import SigiAlert, Config


@admin.register(SigiAlert)
class SigiAlertAdmin(admin.ModelAdmin):
    list_display = ("titulo", "caminho", "destinatarios")
    search_fields = ("titulo", "caminho")
    formfield_overrides = {HTMLField: {"widget": AdminTinyMCE}}
    list_filter = ("destinatarios",)


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ["parametro", "valor"]
    list_filter = ["parametro"]
