# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _
from localflavor.br.forms import BRZipCodeField

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.servidores.models import Servidor


class CasaLegislativaForm(forms.ModelForm):
    # cnpj = BRCNPJField(
    #    label=_(u'CNPJ'),
    #    required=False,
    #    help_text=_(u'Utilize o formato <em>XX.XXX.XXX/XXXX-XX</em> ou insira apenas os dígitos.')
    #)
    cep = BRZipCodeField(label=_(u'CEP'), help_text=_(u'Formato') + ': <em>XXXXX-XXX</em>.')

    class Meta:
        model = CasaLegislativa
        fields = '__all__'
        
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
