import pathlib
from django import template
from django.conf import settings
from django.db import models
from django.templatetags.static import static

register = template.Library()

ICONS_FOLDER = settings.STATIC_ROOT / "img/icons/"


@register.filter
def file_image(value):
    if not isinstance(value, models.fields.files.FieldFile):
        return value
    if is_image(value):
        return value.url or static("img/icons/unknown.jpg")
    sufixo = pathlib.Path(value.name).suffix[1:]
    if (ICONS_FOLDER / f"{sufixo}.jpg").exists():
        return static(f"img/icons/{sufixo}.jpg")
    else:
        return static("img/icons/unknown.jpg")


@register.filter
def is_image(value):
    return isinstance(value, models.fields.files.ImageFieldFile)
