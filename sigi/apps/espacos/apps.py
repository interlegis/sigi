from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EspacosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "espacos"
    name = "sigi.apps.espacos"
    verbose_name = _("Agenda de espaços")

    def ready(self):
        from . import signals

        return super().ready()
