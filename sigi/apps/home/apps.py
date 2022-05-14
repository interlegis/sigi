from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sigi.apps.home"
    verbose_name = _("Home page do SIGI")
