import re
from unicodedata import normalize
from django.contrib import admin as django_admin
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.template.loader import render_to_string
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


def editor_help(field_name, Field_list):
    placeholders = []
    for name, detail in Field_list:
        if type(detail) is str:
            placeholders.append([f"{{{{ {name} }}}}", detail])
        else:
            placeholders.append(
                [
                    f"{{{{ {name} }}}}",
                    detail._meta.verbose_name.capitalize(),
                ]
            )
            for field in detail._meta.fields:
                if field.auto_created or type(field) is models.ForeignKey:
                    pass  # Ignore FK and auto-PK
                else:
                    placeholders.append(
                        [f"{{{{ {name}.{field.name} }}}}", field.verbose_name]
                    )

    return render_to_string(
        "home/editor_help_snippet.html",
        {"field_name": field_name, "placeholders": placeholders},
    )


def abreviatura(name):
    for conector in [" da ", " de ", " do ", " das ", " dos ", " e "]:
        name = name.replace(conector, " ")
    return ("".join([w[0] for w in name.split()])).upper()


def valida_cnpj(cnpj):
    cnpj = re.sub(r"[^\d]", "", cnpj).zfill(14)
    if cnpj == (cnpj[0] * len(cnpj)):
        return False
    calc_dv = f"{0 if 11-(sum([(i%8+2)*int(d) for i, d in enumerate(reversed(list(cnpj[:-2])))])%11) >= 10 else 11-(sum([(i%8+2)*int(d) for i, d in enumerate(reversed(list(cnpj[:-2])))])%11)}{0 if 11-(sum([(i%8+2)*int(d) for i, d in enumerate(reversed(list(cnpj[:-1])))])%11) >= 10 else 11-(sum([(i%8+2)*int(d) for i, d in enumerate(reversed(list(cnpj[:-1])))])%11)}"
    return calc_dv == cnpj[-2:]


def mask_cnpj(cnpj):
    if cnpj == "":
        return ""
    cnpj = re.sub(r"[^\d]", "", cnpj).zfill(14)
    return re.sub(
        r"(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})", r"\1.\2.\3/\4-\5", cnpj
    )
