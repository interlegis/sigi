import datetime
import docutils.core
import traceback
from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_extensions.management.jobs import BaseJob
from sigi.apps.utils.models import Config


class MisconfiguredError(Exception):
    pass


class QuarterDailyJob(BaseJob):
    when = "quarter_daily"


class AdminJobMixin:
    _sys_user = None

    def get_sys_user(self):
        if self._sys_user is None:
            try:
                from sigi.apps.servidores.models import Servidor

                self._sys_user = Servidor.objects.get(sigi=True).user
            except Exception:
                pass
        return self._sys_user

    def _admin_log(self, object, action_flag, message=""):
        sys_user = self.get_sys_user()
        if sys_user is None:
            return  # No admin log
        LogEntry.objects.log_action(
            user_id=sys_user.id,
            content_type_id=ContentType.objects.get_for_model(type(object)).pk,
            object_id=object.pk,
            object_repr=str(object),
            action_flag=action_flag,
            change_message=message,
        )

    def admin_log_addition(self, object, message=""):
        self._admin_log(object, ADDITION, message)

    def admin_log_change(self, object, message=""):
        self._admin_log(object, CHANGE, message)
