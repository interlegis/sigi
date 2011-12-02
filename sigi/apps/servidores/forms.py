# -*- coding: utf8 -*-

from django import forms

from sigi.apps.utils.validators import valida_data, valida_periodo_data

from sigi.apps.servidores.models import Ferias, Licenca, Funcao, Servidor


class FeriasForm(forms.ModelForm):
    class Meta:
        model = Ferias

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_ferias'), data.get('fim_ferias')):
            raise forms.ValidationError(u"""A data de início deve ser menor
                que a data final. Verifique novamente""")
        return data


class LicencaForm(forms.ModelForm):
    class Meta:
        model = Licenca

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_licenca'), data.get('fim_licenca')):
            raise forms.ValidationError(u"""A data de início deve ser menor
            que a data final. Verifique novamente""")
        return data


class FuncaoForm(forms.ModelForm):
    class Meta:
        model = Funcao

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_funcao'), data.get('fim_funcao')):
            raise forms.ValidationError(u"""A data de início deve ser menor
            que a data final. Verifique
            novamente""")

        # Verifica na função anterior, se o seu período é igual
        # ou está entre o período da função atual.
        servidor = Servidor.objects.get(nome_completo=data.get('servidor'))
        if len(servidor.funcao_set.all()):
            if len(servidor.funcao_set.all()) > 1:
                funcao_anterior = servidor.funcao_set.all()[1]
            elif len(servidor.funcao_set.all()) == 1:
                funcao_anterior = servidor.funcao_set.all()[0]

            if valida_periodo_data(funcao_anterior.inicio_funcao,
                funcao_anterior.fim_funcao, data.get('inicio_funcao'),
                data.get('fim_funcao')):
                raise forms.ValidationError(u"""Você não pode exercer
                uma função no mesmo período que a anterior, como também,
                não pode ser entre o período da mesma.""")
        return data
