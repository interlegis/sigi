# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

from captcha.fields import CaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Layout, Submit
from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm)
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from easy_select2 import Select2

import sigi.apps.crispy_layout_mixin
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.crispy_layout_mixin import form_actions
from sigi.apps.crud.utils import YES_NO_CHOICES

from .models import Telefone, Usuario


class ResponsavelForm(ModelForm):
    responsavel = forms.TypedChoiceField(
        widget=forms.Select(),
        label=_(u'Responsavel?'),
        choices=YES_NO_CHOICES)

    class Meta(object):
        model = Usuario
        fields = ['responsavel']

    def __init__(self, *args, **kwargs):
        super(ResponsavelForm, self).__init__(*args, **kwargs)
        row1 = sigi.apps.crispy_layout_mixin.to_row([(u'responsavel', 12)])

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(_(u'Atestar Responsável'),
                     HTML(u'''<p align="center"><font size="4" color="red">
                          Ao atestar o vínculo deste usuário com esta casa você
                          estará assumindo responsabilidade por qualquer
                          problema que poderá ocorrer pela existência de dados
                          incorretos.</font></p>'''),
                     row1,
                     form_actions(
                     save_label='Atestar')))


class ConveniadoForm(ModelForm):
    conveniado = forms.TypedChoiceField(
        widget=forms.Select(),
        label=_(u'Conveniado?'),
        choices=YES_NO_CHOICES)

    class Meta(object):
        model = Usuario
        fields = ['conveniado']

    def __init__(self, *args, **kwargs):
        super(ConveniadoForm, self).__init__(*args, **kwargs)
        row1 = sigi.apps.crispy_layout_mixin.to_row([(u'conveniado', 12)])

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(_(u'Atestar Conveniado'),
                     HTML(u'''<p align="center"><font size="4" color="red">
                          Ao atestar o convênio desta casa você estará
                          assumindo resonsabilidade por qualquer problema
                          que poderá ocorrer pela existência de dados
                          incorretos.</font></p>'''),
                     row1,
                     form_actions(
                     save_label='Atestar')))


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=u"Username", max_length=30,
        widget=forms.TextInput(
            attrs={u'class': u'form-control', u'name': u'username'}))

    password = forms.CharField(
        label=u"Password", max_length=30,
        widget=forms.PasswordInput(
            attrs={u'class': u'form-control', u'name': u'password'}))


class UsuarioForm(ModelForm):
    # Telefone
    TIPO_TELEFONE = [(u'FIXO', u'FIXO'), (u'CELULAR', u'CELULAR')]

    # Primeiro Telefone
    primeiro_tipo = forms.ChoiceField(
        widget=forms.Select(),
        choices=TIPO_TELEFONE,
        label=_(u'Tipo Telefone'))
    primeiro_ddd = forms.CharField(max_length=2, label=_(u'DDD'))
    primeiro_numero = forms.CharField(max_length=10, label=_(u'Número'))
    primeiro_principal = forms.TypedChoiceField(
        widget=forms.Select(),
        label=_(u'Telefone Principal?'),
        choices=YES_NO_CHOICES)

    # Primeiro Telefone
    segundo_tipo = forms.ChoiceField(
        required=False,
        widget=forms.Select(),
        choices=TIPO_TELEFONE,
        label=_(u'Tipo Telefone'))
    segundo_ddd = forms.CharField(
        required=False,
        max_length=2,
        label=_(u'DDD'))
    segundo_numero = forms.CharField(
        required=False, max_length=10, label=_(u'Número'))
    segundo_principal = forms.ChoiceField(
        required=False,
        widget=forms.Select(),
        label=_(u'Telefone Principal?'),
        choices=YES_NO_CHOICES)

    # Usuário
    password = forms.CharField(
        max_length=20,
        label=_(u'Senha'),
        widget=forms.PasswordInput())

    password_confirm = forms.CharField(
        max_length=20,
        label=_(u'Confirmar Senha'),
        widget=forms.PasswordInput())

    email_confirm = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={u'style': u'text-transform:lowercase;'}),
        label=_(u'Confirmar Email'))

    captcha = CaptchaField()

    casa_legislativa = forms.ModelChoiceField(
        queryset=CasaLegislativa.objects.all(),
        widget=Select2()
    )

    class Meta(object):
        model = Usuario
        fields = [u'username', u'email', u'nome_completo', u'password',
                  u'vinculo', u'password_confirm', u'email_confirm',
                  u'captcha', u'cpf', u'rg', u'cargo', u'casa_legislativa']

        widgets = {u'email': forms.TextInput(
                   attrs={u'style': u'text-transform:lowercase;'}), }

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        self.fields[u'rg'].widget.attrs[u'class'] = u'rg'
        self.fields[u'cpf'].widget.attrs[u'class'] = u'cpf'
        self.fields[u'primeiro_numero'].widget.attrs[u'class'] = u'telefone'
        self.fields[u'primeiro_ddd'].widget.attrs[u'class'] = u'ddd'
        self.fields[u'segundo_numero'].widget.attrs[u'class'] = u'telefone'
        self.fields[u'segundo_ddd'].widget.attrs[u'class'] = u'ddd'

    def valida_igualdade(self, texto1, texto2, msg):
        if texto1 != texto2:
            raise ValidationError(msg)
        return True

    def clean_username(self):
        # import ipdb; ipdb.set_trace()
        usuario = User.objects.filter(
            username=self.cleaned_data[u'username']).exists()

        if usuario:
            raise ValidationError(u'Usuário existente.')

        return self.cleaned_data[u'username']

    def clean_primeiro_numero(self):
        cleaned_data = self.cleaned_data

        telefone = Telefone()
        telefone.tipo = self.data[u'primeiro_tipo']
        telefone.ddd = self.data[u'primeiro_ddd']
        telefone.numero = self.data[u'primeiro_numero']
        telefone.principal = self.data[u'primeiro_principal']

        cleaned_data[u'primeiro_telefone'] = telefone
        return self.cleaned_data[u'primeiro_numero']

    def clean_segundo_numero(self):
        cleaned_data = self.cleaned_data

        telefone = Telefone()
        telefone.tipo = self.data[u'segundo_tipo']
        telefone.ddd = self.data[u'segundo_ddd']
        telefone.numero = self.data[u'segundo_numero']
        telefone.principal = self.data[u'segundo_principal']

        cleaned_data[u'segundo_telefone'] = telefone
        return self.cleaned_data[u'segundo_numero']

    def valida_email_existente(self):
        return Usuario.objects.filter(
            email=self.cleaned_data[u'email']).exists()

    def clean(self):
        if (u'password' not in self.cleaned_data or
                u'password_confirm' not in self.cleaned_data):
            raise ValidationError(_(u'Favor informar senhas atuais ou novas'))

        msg = _(u'As senhas não conferem.')
        self.valida_igualdade(
            self.cleaned_data[u'password'],
            self.cleaned_data[u'password_confirm'],
            msg)

        if (u'email' not in self.cleaned_data or
                u'email_confirm' not in self.cleaned_data):
            raise ValidationError(_(u'Favor informar endereços de email'))

        msg = _(u'Os emails não conferem.')
        self.valida_igualdade(
            self.cleaned_data[u'email'],
            self.cleaned_data[u'email_confirm'],
            msg)

        email_existente = self.valida_email_existente()

        if email_existente:
            msg = _(u'Esse email já foi cadastrado.')
            raise ValidationError(msg)

        try:
            validate_password(self.cleaned_data[u'password'])
        except ValidationError, error:
            raise ValidationError(error)

        return self.cleaned_data

    @transaction.atomic
    def save(self, commit=False):
        usuario = super(UsuarioForm, self).save(commit)

        # Cria telefones
        tel = Telefone.objects.create(
            tipo=self.data[u'primeiro_tipo'],
            ddd=self.data[u'primeiro_ddd'],
            numero=self.data[u'primeiro_numero'],
            principal=self.data[u'primeiro_principal']
        )
        usuario.primeiro_telefone = tel

        tel = self.cleaned_data[u'segundo_telefone']
        if (tel.tipo and tel.ddd and tel.numero and tel.principal):
            tel = Telefone.objects.create(
                tipo=self.data[u'segundo_tipo'],
                ddd=self.data[u'segundo_ddd'],
                numero=self.data[u'segundo_numero'],
                principal=self.data[u'segundo_principal']
            )
            usuario.segundo_telefone = tel

        # Cria User
        u = User.objects.create(username=usuario.username, email=usuario.email)
        u.set_password(self.cleaned_data[u'password'])
        u.is_active = False

        u.save()
        usuario.user = u
        usuario.save()
        return usuario


class UsuarioEditForm(UsuarioForm):
    captcha = CaptchaField(required=False)

    casa_legislativa = forms.ModelChoiceField(
        queryset=CasaLegislativa.objects.all(),
        widget=Select2(),
        required=False
    )

    class Meta(object):
        model = Usuario
        fields = [u'username', u'email', u'nome_completo', u'vinculo',
                  u'email_confirm', u'cpf', u'rg', u'cargo']
        exclude = [u'captcha', u'casa_legislativa']

        widgets = {u'username': forms.TextInput(
                   attrs={u'readonly': u'readonly'}),
                   u'nome_completo': forms.TextInput(
                   attrs={u'readonly': u'readonly'}),
                   u'cpf': forms.TextInput(
                   attrs={u'readonly': u'readonly'}),
                   u'rg': forms.TextInput(
                   attrs={u'readonly': u'readonly'}),
                   u'email': forms.TextInput(
                   attrs={u'style': u'text-transform:lowercase;'}), }

    def __init__(self, *args, **kwargs):
        super(UsuarioEditForm, self).__init__(*args, **kwargs)
        self.fields[u'email_confirm'].initial = self.instance.email
        self.fields.pop(u'password')
        self.fields.pop(u'password_confirm')

    def clean_username(self):
        pass

    def valida_email_existente(self):
        u'''Não permite atualizar emails para
           emails existentes de outro usuário
        '''

        return Usuario.objects.filter(
            email=self.cleaned_data[u'email']).exclude(
            user__username=self.data[u'username']).exists()

    def clean(self):
        self.cleaned_data[u'username'] = self.data[u'username']
        if (u'email' not in self.cleaned_data or
                u'email_confirm' not in self.cleaned_data):
            raise ValidationError(_(u'Favor informar endereços de email'))

        msg = _(u'Os emails não conferem.')
        self.valida_igualdade(
            self.cleaned_data[u'email'],
            self.cleaned_data[u'email_confirm'],
            msg)
        email_existente = self.valida_email_existente()

        if email_existente:
            msg = _(u'Esse email já foi cadastrado.')
            raise ValidationError(msg)

        return self.cleaned_data

    @transaction.atomic
    def save(self, commit=False):
        usuario = super(UsuarioForm, self).save(commit)

        # Primeiro telefone
        tel = usuario.primeiro_telefone

        tel.tipo = self.data[u'primeiro_tipo']
        tel.ddd = self.data[u'primeiro_ddd']
        tel.numero = self.data[u'primeiro_numero']
        tel.principal = self.data[u'primeiro_principal']
        tel.save()

        usuario.primeiro_telefone = tel

        # Segundo telefone
        tel = usuario.segundo_telefone

        if tel:
            tel.tipo = self.data[u'segundo_tipo']
            tel.ddd = self.data[u'segundo_ddd']
            tel.numero = self.data[u'segundo_numero']
            tel.principal = self.data[u'segundo_principal']
            tel.save()
            usuario.segundo_telefone = tel

        tel = self.cleaned_data[u'segundo_telefone']
        if (tel.tipo and tel.ddd and tel.numero and tel.principal):
            tel = Telefone.objects.create(
                tipo=self.data[u'segundo_tipo'],
                ddd=self.data[u'segundo_ddd'],
                numero=self.data[u'segundo_numero'],
                principal=self.data[u'segundo_principal']
            )
            usuario.segundo_telefone = tel

        # User
        u = usuario.user
        u.email = usuario.email
        u.save()

        usuario.data_ultima_atualizacao = datetime.now()
        usuario.save()
        return usuario


class HabilitarEditForm(ModelForm):
    habilitado = forms.ChoiceField(
        widget=forms.Select(),
        required=True,
        choices=YES_NO_CHOICES)

    class Meta(object):
        model = Usuario
        fields = [u'cpf', u'nome_completo', u'email', u'habilitado']
        widgets = {
            u'cpf': forms.TextInput(attrs={u'readonly': u'readonly'}),
            u'nome_completo': forms.TextInput(attrs={u'readonly': u'readonly'}
                                              ),
            u'email': forms.TextInput(attrs={u'readonly': u'readonly'})
        }

    def __init__(self, *args, **kwargs):
        super(HabilitarEditForm, self).__init__(*args, **kwargs)
        row1 = sigi.apps.crispy_layout_mixin.to_row(
            [(u'nome_completo', 4),
             (u'cpf', 4),
             (u'email', 4)])
        row2 = sigi.apps.crispy_layout_mixin.to_row([(u'habilitado', 12)])
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _(u'Editar usuário'), row1, row2, form_actions(
                    more=[
                        Submit(
                            u'Cancelar',
                            u'Cancelar',
                            style=u'background-color:black; color:white;')])
            )
        )


class MudarSenhaForm(ModelForm):

    password = forms.CharField(
        max_length=20,
        label=_(u'Nova Senha'),
        widget=forms.PasswordInput())

    password_confirm = forms.CharField(
        max_length=20,
        label=_(u'Confirmar Nova Senha'),
        widget=forms.PasswordInput())

    captcha = CaptchaField()

    def valida_igualdade(self, texto1, texto2, msg):
        if texto1 != texto2:
            raise ValidationError(msg)
        return True

    def clean(self):
        if (u'password' not in self.cleaned_data or
                u'password_confirm' not in self.cleaned_data):
            raise ValidationError(_(u'Favor informar senhas atuais \
                                     ou novas'))

        msg = _(u'As senhas não conferem.')
        self.valida_igualdade(
            self.cleaned_data[u'password'],
            self.cleaned_data[u'password_confirm'],
            msg)

        try:
            validate_password(self.cleaned_data[u'password'])
        except ValidationError, error:
            raise ValidationError(error)

    class Meta(object):
        model = Usuario
        fields = [u'password', u'password_confirm', u'captcha']

    def __init__(self, *args, **kwargs):
        super(MudarSenhaForm, self).__init__(*args, **kwargs)
        row1 = sigi.apps.crispy_layout_mixin.to_row(
            [(u'password', 6),
             (u'password_confirm', 6)])
        row2 = sigi.apps.crispy_layout_mixin.to_row([(u'captcha', 12)])
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _(u'Mudar Senha'), row1, row2,
                form_actions(
                    more=[
                        Submit(
                            u'Cancelar',
                            u'Cancelar',
                            style=u'background-color:black; color:white;')])
            )
        )


class RecuperarSenhaEmailForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super(RecuperarSenhaEmailForm, self).__init__(*args, **kwargs)
        row1 = sigi.apps.crispy_layout_mixin.to_row(
            [(u'email', 6)])
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(_(u'Recuperar Senha'),
                     row1,
                     form_actions(
                     more=[Submit(u'Cancelar',
                                  u'Cancelar',
                                  style=u'background-color:black;'
                                        'color:white;')])))

    def clean(self):
        email_existente_usuario = Usuario.objects.filter(
            email=self.cleaned_data[u'email'])
        email_existente_user = User.objects.filter(
            email=self.cleaned_data[u'email'])

        if not email_existente_usuario and not email_existente_user:
            msg = _(u'Não existe nenhum usuário cadastrado com este e-mail.')
            raise ValidationError(msg)

        return self.cleaned_data


class RecuperacaoMudarSenhaForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(RecuperacaoMudarSenhaForm, self).__init__(*args, **kwargs)
        self.fields[u'new_password1'].help_text = u''
        row1 = sigi.apps.crispy_layout_mixin.to_row(
            [(u'new_password1', 6),
             (u'new_password2', 6)])
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(_(u''),
                     row1,
                     form_actions(
                     more=[Submit(u'Cancelar',
                                  u'Cancelar',
                                  style=u'background-color:black;'
                                        'color:white;')])))
