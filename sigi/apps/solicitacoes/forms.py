from __future__ import absolute_import

import json

import requests
from django import forms
from django.db import transaction
from django.forms import ModelForm

from sigi.settings.prod import OSTICKET_API_KEY, OSTICKET_ATENDIMENTO_URL

from .models import Solicitacao


def open_osticket(solicitacao):
    headers = {'X-API-KEY': OSTICKET_API_KEY,
               'Content-Type': 'application/json'}

    data = {"alert": True,
            "autorespond": True,
            "source": "API",
            "name": solicitacao.usuario.username,
            "email": solicitacao.usuario.email,
            "phone": ' - '.join(
                (solicitacao.usuario.primeiro_telefone.ddd,
                 solicitacao.usuario.primeiro_telefone.numero)),
            "subject": solicitacao.titulo,
            "ip": "",
            "message": solicitacao.resumo}
    response = requests.post(OSTICKET_ATENDIMENTO_URL,
                             headers=headers, json=data)
    if response.status_code == requests.codes.created:
        return response.text
    else:
        response.raise_for_status()


class SolicitacaoForm(ModelForm):

    resumo = forms.CharField(
        label=u'Resumo',
        max_length=500,
        widget=forms.Textarea)

    class Meta:
        model = Solicitacao
        fields = [u'usuario', u'sistema',
                  u'email_contato', u'telefone_contato',
                  u'casa_legislativa', u'titulo', u'resumo']
        widgets = {
            u'usuario': forms.HiddenInput(),
            u'casa_legislativa': forms.TextInput(
                attrs={'readonly': 'readonly'}),
            u'email_contato': forms.TextInput(
                attrs={'readonly': 'readonly'}),
            u'telefone_contato': forms.TextInput(
                attrs={'readonly': 'readonly'})
        }

    @transaction.atomic
    def save(self, commit=False):
        solicitacao = super(SolicitacaoForm, self).save(commit)
        os_ticket = open_osticket(solicitacao)
        solicitacao.osticket = os_ticket
        solicitacao.save()
        return solicitacao
