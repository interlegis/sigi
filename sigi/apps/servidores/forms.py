# -*- coding: utf-8 -*-
from collections import namedtuple

from django import forms
from django.utils.translation import ugettext as _

from sigi.apps.servidores.models import Ferias, Funcao, Licenca, Servidor


def valida_data_inicial_menor_que_final(data, chave_ini, chave_fim):
    if data.get(chave_ini) >= data.get(chave_fim):
        raise forms.ValidationError(_(
            u"A data de início deve ser menor que a data final. Verifique novamente"))


class FeriasForm(forms.ModelForm):

    class Meta:
        model = Ferias
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        valida_data_inicial_menor_que_final(data, 'inicio_ferias', 'fim_ferias')
        return data


class LicencaForm(forms.ModelForm):

    class Meta:
        model = Licenca
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        valida_data_inicial_menor_que_final(data, 'inicio_licenca', 'fim_licenca')
        return data


Periodo = namedtuple('Periodo', ['ini', 'fim'])


def periodos_se_sobrepoe(periodo1, periodo2):
    return not (periodo1.fim < periodo2.ini or periodo2.fim < periodo1.ini)


class FuncaoForm(forms.ModelForm):

    class Meta:
        model = Funcao
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        valida_data_inicial_menor_que_final(data, 'inicio_funcao', 'fim_funcao')

        # Verifica na função anterior, se o seu período é igual
        # ou está entre o período da função atual.
        servidor = Servidor.objects.get(nome_completo=data.get('servidor'))
        for funcao in servidor.funcao_set.all():
            if periodos_se_sobrepoe(
                    Periodo(funcao.inicio_funcao, funcao.fim_funcao),
                    Periodo(data.get('inicio_funcao'), data.get('fim_funcao'))):
                raise forms.ValidationError(_(
                    u"Este período coincide com o de outra função exercida."))
        return data
