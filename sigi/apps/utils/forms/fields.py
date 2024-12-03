import datetime
from django.forms import fields
from django.utils.translation import gettext_lazy as _
from sigi.apps.utils.forms import widgets


class MonthField(fields.DateField):
    widget = widgets.MonthInput
    input_formats = ["%Y-%m", "%m-%Y"]
    default_error_messages = {
        "invalid": _("Enter a valid month."),
    }

    def strptime(self, value, format):
        return datetime.datetime.strptime(value, format).date()
