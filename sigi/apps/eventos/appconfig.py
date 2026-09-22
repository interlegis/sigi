from django import forms
from django.utils.translation import gettext_lazy as _


class AppConfigForm(forms.Form):
    encerra_inscricao = forms.IntegerField(
        min_value=0,
        required=True,
        label=_("Encerra inscrições de oficinas no Portal"),
        initial=30,
        help_text=_(
            "Número de dias a esperar após o término da oficina antes de "
            "a remover do Portal Interlegis"
        ),
    )
