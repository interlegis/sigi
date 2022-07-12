from django.contrib import admin
from sigi.apps.utils.models import SigiAlert
from tinymce.models import HTMLField
from tinymce.widgets import AdminTinyMCE


@admin.register(SigiAlert)
class SigiAlertAdmin(admin.ModelAdmin):
    list_display = ("titulo", "caminho", "destinatarios")
    search_fields = ("titulo", "caminho")
    formfield_overrides = {HTMLField: {"widget": AdminTinyMCE}}
    list_filter = ("destinatarios",)
