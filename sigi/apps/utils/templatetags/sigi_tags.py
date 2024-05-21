import datetime
from django import template
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

register = template.Library()


@register.filter
def interval(value, arg):
    if not isinstance(value, datetime.datetime) or not isinstance(
        arg, datetime.datetime
    ):
        return ""
    value = timezone.localtime(value)
    arg = timezone.localtime(arg)
    if value.year != arg.year:
        format_mask = "%d/%m/%Y às %H:%M"
    elif value.month != arg.month:
        format_mask = "%d/%m às %H:%M"
    elif value.day != arg.day:
        format_mask = "dia %d às %H:%M"
    else:
        format_mask = "%H:%M"
    return _(
        f"de {value.strftime(format_mask)} " f"a {arg.strftime(format_mask)}"
    )


@register.filter
def sum(value, arg):
    return value + arg


@register.simple_tag
def multiply(value, arg):
    return value * arg


@register.filter
def valueof(obj, attr_name):
    if hasattr(obj, attr_name):
        return getattr(obj, attr_name)
    if isinstance(obj, models.Model):
        for part in attr_name.split("__"):
            obj = getattr(obj, part)
        return str(obj)
