# -*- coding: utf8 -*-

from django import forms

from sigi.apps.utils.validators import valida_data

from sigi.apps.servidores.models import Ferias, Licenca, Funcao

class FeriasForm(forms.ModelForm):
    class Meta:
        model = Ferias

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_ferias'), data.get('fim_ferias')):
            raise forms.ValidationError(
                u"""A data de início deve ser menor que a data final. Verifique
                novamente""")
        return data


class LicencaForm(forms.ModelForm):
    class Meta:
        model = Licenca

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_licenca'), data.get('fim_licenca')):
            raise forms.ValidationError(
                u"""A data de início deve ser menor que a data final. Verifique
                novamente""")
        return data


class FuncaoForm(forms.ModelForm):
    class Meta:
        model = Funcao

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_funcao'), data.get('fim_funcao')):
            raise forms.ValidationError(
                u"""A data de início deve ser menor que a data final. Verifique
                novamente""")
        return data
