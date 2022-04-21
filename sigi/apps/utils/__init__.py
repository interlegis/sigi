from unicodedata import normalize
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.encoding import force_str


class SearchField(models.TextField):
    def pre_save(self, model_instance, add):
        search_text = []
        for field_name in self.field_names:
            val = force_str(to_ascii(getattr(model_instance, field_name)))
            search_text.append(val)
        value = " ".join(search_text)
        setattr(model_instance, self.name, value)
        return value

    def __init__(self, field_names, *args, **kwargs):
        self.field_names = field_names
        kwargs["editable"] = False
        super(self.__class__, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(SearchField, self).deconstruct()
        kwargs["field_names"] = self.field_names
        return name, path, args, kwargs


def to_ascii(txt, codif="utf-8"):
    if not isinstance(txt, str):
        txt = force_str(txt)
    if isinstance(txt, str):
        txt = txt.encode("utf-8")
    return (
        normalize("NFKD", txt.decode(codif))
        .encode("ASCII", "ignore")
        .decode(codif)
    )


def queryset_ascii(self, request):
    if "q" in request.GET:
        request.GET._mutable = True
        request.GET["q"] = to_ascii(request.GET["q"])
    return admin.ModelAdmin.get_queryset(self, request)


def field_label(name, model):
    name = name.split("__")
    try:
        field = model._meta.get_field(name[0])
    except FieldDoesNotExist:
        return force_str(" ".join(name))

    try:
        label = force_str(field.verbose_name)
    except AttributeError:
        # field is likely a RelatedObject
        label = force_str(field.name).capitalize()
    if len(name) > 1:
        to_model = field.get_path_info()[0].to_opts.model
        label = label + "/" + field_label("__".join(name[1:]), to_model)

    return label
