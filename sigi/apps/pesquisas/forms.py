# -*- coding: utf-8 -*-

from forms_builder.forms.forms import FormForForm
from sigi.apps.pesquisas.models import Formulario, Resposta

class PesquisaForm(FormForForm):
    field_entry_model = Resposta

    class Meta(FormForForm.Meta):
        model = Formulario
        fields = ['casa_legislativa',]    