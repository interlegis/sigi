# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _
from sigi.apps.eventos.models import ModeloDeclaracao

class SelecionaModeloForm(forms.Form):
    modelo = forms.ModelChoiceField(
        queryset=ModeloDeclaracao.objects.all(),
        required=True,
        label=_(u"Modelo de declaração"),
    )