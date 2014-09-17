# -*- coding: utf-8 -*-
from django import forms
from localflavor.br.forms import BRZipCodeField
from sigi.apps.casas.models import CasaLegislativa


class CasaLegislativaForm(forms.ModelForm):
    #cnpj = BRCNPJField(
    #    label='CNPJ',
    #    required=False,
    #    help_text='Utilize o formato <em>XX.XXX.XXX/XXXX-XX</em> ou '
    #              'insira apenas os dígitos.'
    #)
    cep = BRZipCodeField(label='CEP', help_text='Formato: <em>XXXXX-XXX</em>.')

    class Meta:
        model = CasaLegislativa
        fields = '__all__'
