from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.filter
def get(d, key_name):
    try:
        value = d[key_name]
    except KeyError:
        value = settings.TEMPLATE_STRING_IF_INVALID
    return value
