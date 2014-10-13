# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from sigi.apps.servidores.models import Ferias, Licenca, Funcao, Servidor
from sigi.apps.utils.validators import valida_data, valida_periodo_data


class FeriasForm(forms.ModelForm):

    class Meta:
        model = Ferias
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_ferias'), data.get('fim_ferias')):
            raise forms.ValidationError(_(u"""A data de início deve ser menor
                que a data final. Verifique novamente"""))
        return data


class LicencaForm(forms.ModelForm):

    class Meta:
        model = Licenca
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_licenca'), data.get('fim_licenca')):
            raise forms.ValidationError(_(u"""A data de início deve ser menor
            que a data final. Verifique novamente"""))
        return data


class FuncaoForm(forms.ModelForm):

    class Meta:
        model = Funcao
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        if valida_data(data.get('inicio_funcao'), data.get('fim_funcao')):
            raise forms.ValidationError(_(u"""A data de início deve ser menor
            que a data final. Verifique
            novamente"""))

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
                raise forms.ValidationError(_(u"""Você não pode exercer
                uma função no mesmo período que a anterior, como também,
                não pode ser entre o período da mesma."""))
        return data
