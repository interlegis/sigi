# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext as _
from localflavor.br.forms import BRZipCodeField

from sigi.apps.casas.models import Orgao
from sigi.apps.servidores.models import Servidor

class AtualizaCasaForm(forms.Form):
    arquivo = forms.FileField(
        required=True,
        label=_(u"arquivo a importar"),
        help_text=_(u"Envie um arquivo no formato CSV"),
    )

class OrgaoForm(forms.ModelForm):
    # cnpj = BRCNPJField(
    #    label=_(u'CNPJ'),
    #    required=False,
    #    help_text=_(u'Utilize o formato <em>XX.XXX.XXX/XXXX-XX</em> ou insira apenas os dígitos.')
    #)
    cep = BRZipCodeField(label=_(u'CEP'), help_text=_(u'Formato') + ': <em>XXXXX-XXX</em>.')

    class Meta:
        model = Orgao
        fields = '__all__'

    # def clean(self):
    #     cleaned_data = super(OrgaoForm, self).clean()
    #     tipo = cleaned_data.get('tipo')
    #     municipio = cleaned_data.get('municipio')
    #     if tipo.legislativo:
    #         if Orgao.objects.filter(tipo=tipo)

class PortfolioForm(forms.Form):
    ACAO_CHOICES = (
        ('ADD', _(u"Adicionar")),
        ('DEL', _(u"Remover"))
    )
    acao = forms.ChoiceField(
        label=_(u"Ação"),
        choices=ACAO_CHOICES,
        initial='ADD',
        widget=forms.RadioSelect
    )
    gerente = forms.ModelChoiceField(
        queryset=Servidor.objects.all(),
        label=_(u"Atribuir para")
    )

    # O label precisa ser trocado dependendo da região que se está visualizando
    def __init__(self, label=_(u"Atribuir para"), *args, **kwargs):
        super(PortfolioForm, self).__init__(*args, **kwargs)
        self.fields['gerente'].label = label
