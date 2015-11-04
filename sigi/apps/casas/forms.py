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
    gerente_contas = forms.ModelChoiceField(queryset=Servidor.objects.all(), label=_(u"Atribuir casas para"))
    
    def __init__(self, label=_(u"Atribuir casas para"), *args, **kwargs):
        super(PortfolioForm, self).__init__(*args, **kwargs)
        self.fields['gerente_contas'].label = label
