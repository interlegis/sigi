from __future__ import absolute_import
from django.db import transaction
from django import forms
from django.forms import ModelForm
from sigi.settings.prod import OSTICKET_API_KEY, OSTICKET_URL
from .models import Solicitacao
import json
import requests


def open_osticket(solicitacao):
    headers = {'X-API-KEY': OSTICKET_API_KEY,
               'Content-Type': 'application/json'}

    usuario = solicitacao.usuario
    data = {"alert": True,
            "autorespond": True,
            "source": "API",
            "name": usuario.username,
            "email": usuario.email,
            "phone": '-'.join((usuario.primeiro_telefone.ddd,
                               usuario.primeiro_telefone.numero)),
            "subject": solicitacao.titulo,
            "ip": "",
            "message": solicitacao.resumo}
    response = requests.post(OSTICKET_URL, headers=headers, json=data)
    if response.status_code == requests.codes.created:
        return response.text
    else:
        response.raise_for_status()


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
        widgets = {
            u'codigo': forms.HiddenInput(),
            u'usuario': forms.HiddenInput(),
            u'casa_legislativa': forms.TextInput(attrs={'readonly':'readonly'}),
            u'email_contato': forms.TextInput(attrs={'readonly':'readonly'}),
            u'telefone_contato': forms.TextInput(attrs={'readonly':'readonly'})
        }

    @transaction.atomic
    def save(self, commit=False):
        solicitacao = super(SolicitacaoForm, self).save(commit)
        os_ticket = open_osticket(solicitacao)
        solicitacao.osticket = os_ticket
        solicitacao.save()
        return solicitacao


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
