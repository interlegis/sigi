from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ParlamentaresConfig(AppConfig):
    name = "sigi.apps.parlamentares"
    verbose_name = _("parlamentares")
