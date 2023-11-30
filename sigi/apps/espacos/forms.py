import calendar
from django.utils import timezone
from django import forms
from material.admin.widgets import MaterialAdminDateWidget
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.translation import gettext as _
from sigi.apps.espacos.models import Espaco


class UsoEspacoReportForm(forms.Form):
    VIRTUAL_ALL = "A"
    VIRTUAL_VIRTUAL = "V"
    VIRTUAL_PRESENCIAL = "P"
    VIRTUAL_CHOICES = (
        (VIRTUAL_ALL, _("All")),
        (VIRTUAL_VIRTUAL, _("Apenas virtual")),
        (VIRTUAL_PRESENCIAL, _("Apenas presencial")),
    )

    class Media:
        css = {"all": ["css/change_form.css"]}
        js = [
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/change_form.js",
            "admin/js/vendor/select2/i18n/pt-BR.js",
            "material/admin/js/widgets/TimeInput.js",
            "admin/js/core.js",
            "/admin/jsi18n/",
        ]

    def get_semana(self):
        return [
            {"first": s[0], "last": s[-1]}
            for s in calendar.Calendar().monthdatescalendar(
                timezone.localdate().year, timezone.localdate().month
            )
            if s[0] <= timezone.localdate() <= s[-1]
        ][0]

    data_inicio = forms.DateField(
        label=_("Data início"), required=True, widget=MaterialAdminDateWidget
    )
    data_fim = forms.DateField(
        label=_("Data fim"), required=True, widget=MaterialAdminDateWidget
    )
    virtual = forms.ChoiceField(
        label=_("Tipo de uso"), choices=VIRTUAL_CHOICES, initial=VIRTUAL_ALL
    )
    agrupar_espacos = forms.BooleanField(
        label=_("Agrupar por espaço"), required=False, initial=False
    )
    espaco = forms.ModelMultipleChoiceField(
        label=_("Espaços"),
        required=True,
        queryset=Espaco.objects.all(),
        widget=CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        semana = self.get_semana()
        self.fields["data_inicio"].initial = semana["first"]
        self.fields["data_fim"].initial = semana["last"]
