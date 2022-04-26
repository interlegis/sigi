from django import template

register = template.Library()


@register.filter
def verbose_name(instance, field_name=""):
    if field_name == "":
        return ""
    return instance._meta.get_field(field_name).verbose_name


@register.filter
def field_value(instance, field_name=""):
    return getattr(instance, field_name, "")
