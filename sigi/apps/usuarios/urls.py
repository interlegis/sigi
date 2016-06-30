from __future__ import absolute_import

from django.conf.urls import include, url
from django.contrib.auth.views import (login, logout, password_reset,
                                       password_reset_complete,
                                       password_reset_confirm,
                                       password_reset_done)
from django.views.generic.base import TemplateView

from sigi.apps.usuarios.forms import (LoginForm, RecuperacaoMudarSenhaForm,
                                      RecuperarSenhaEmailForm)
from sigi.apps.usuarios.views import (ConfirmarEmailView, ConveniadoListView,
                                      ConveniadoView, HabilitarDetailView,
                                      HabilitarEditView, MudarSenhaView,
                                      ResponsavelListView, ResponsavelView,
                                      UsuarioCrud)

from .apps import AppConfig

app_name = AppConfig.name

EMAIL_SEND_USER = 'atendimento@interlegis.leg.br'

recuperar_email = [
    url(ur'^atendimento/recuperar/recuperar_senha/$',
        password_reset,
        {u'template_name': u'usuarios/recuperar_senha.html',
         u'password_reset_form': RecuperarSenhaEmailForm,
         u'post_reset_redirect': u'usuarios:recuperar_senha_finalizado',
         u'email_template_name': u'usuarios/recuperar_senha_email.html',
         u'from_email': EMAIL_SEND_USER,
         u'html_email_template_name': u'usuarios/recuperar_senha_email.html'},
        name=u'recuperar_senha'),
    url(ur'^atendimento/recuperar/recuperar_recuperar/finalizado/$',
        password_reset_done,
        {u'template_name': u'usuarios/recuperar_senha_enviado.html'},
        name=u'recuperar_senha_finalizado'),
    url(ur'^atendimento/recuperar/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        password_reset_confirm,
        {u'post_reset_redirect': u'usuarios:recuperar_senha_completo',
         u'template_name': u'usuarios/recuperacao_senha_form.html',
         u'set_password_form': RecuperacaoMudarSenhaForm},
        name=u'recuperar_senha_confirma'),
    url(ur'^atendimento/recuperar/completo/$',
        password_reset_complete,
        {u'template_name': u'usuarios/recuperacao_senha_completo.html'},
        name=u'recuperar_senha_completo'),
]

urlpatterns = recuperar_email + [
    url(ur'^atendimento/login/$', login, {
        u'template_name': u'usuarios/login.html',
        u'authentication_form': LoginForm},
        name=u'login'),
    url(ur'^atendimento/logout/$', logout, {u'next_page': u'/atendimento'},
        name=u'logout'),
    url(ur'^atendimento/usuario/', include(UsuarioCrud.get_urls())),

    url(ur'^atendimento/habilitar/(?P<pk>\d+)$',
        HabilitarDetailView.as_view(), name=u'habilitar_detail'),
    url(ur'^atendimento/habilitar/(?P<pk>\d+)/edit$',
        HabilitarEditView.as_view(), name=u'habilitar_edit'),
    url(ur'^atendimento/usuario/(?P<pk>\d+)/mudar_senha$',
        MudarSenhaView.as_view(), name=u'mudar_senha'),
    url(ur'^usuario/confirmar/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        ConfirmarEmailView.as_view(), name=u'confirmar_email'),

    url(ur'^atesto/responsavel$', ResponsavelListView.as_view(),
        name=u'responsavel_list'),
    url(ur'^atesto/responsavel/(?P<pk>\d+)/$', ResponsavelView.as_view(),
        name=u'responsavel_update'),

    url(ur'^atesto/convenio$', ConveniadoListView.as_view(),
        name=u'convenio_list'),
    url(ur'^atesto/convenio/(?P<pk>\d+)/$', ConveniadoView.as_view(),
        name=u'convenio_update'),
]
