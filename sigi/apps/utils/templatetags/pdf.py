from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def page_break():
    return mark_safe('<div class="new-page"></div>')
