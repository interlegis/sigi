from __future__ import absolute_import
from django import forms
from django.forms import ModelForm

from .models import Sistema, Solicitacao


class SolicitacaoForm(ModelForm):

    resumo = forms.CharField(
        label=u'Resumo',
        max_length=500,
        widget=forms.Textarea)

    class Meta(object):
        model = Solicitacao
        fields = [u'codigo', u'usuario', u'sistema',
                  u'email_contato', u'telefone_contato',
                  u'casa_legislativa', u'titulo', u'resumo']
        widgets = {u'codigo': forms.HiddenInput(),
                   u'usuario': forms.HiddenInput()}


class SolicitacaoEditForm(ModelForm):

    resumo = forms.CharField(
        label=u'Resumo',
        max_length=500,
        widget=forms.Textarea)

    class Meta(object):
        model = Solicitacao
        fields = [u'codigo', u'usuario', u'sistema',
                  u'casa_legislativa', u'titulo', u'resumo']
        widgets = {u'codigo': forms.TextInput(attrs={u'readonly': u'readonly'}),
                   u'usuario': forms.HiddenInput()}


class SistemaForm(ModelForm):

    class Meta(object):
        model = Sistema
        fields = [u'sigla', u'nome']
