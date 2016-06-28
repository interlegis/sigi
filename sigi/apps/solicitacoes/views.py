from __future__ import absolute_import

import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse

import sigi.apps.crud.base
from sigi.apps.crud.base import (Crud, CrudBaseMixin, CrudCreateView,
                                 CrudListView, CrudUpdateView)
from sigi.apps.usuarios.models import Usuario

from .forms import SolicitacaoForm
from .models import Solicitacao
from sigi.context_processors import recupera_usuario


class SolicitacaoCrud(LoginRequiredMixin, Crud):
    model = Solicitacao
    help_path = u''

    class ListView(LoginRequiredMixin, CrudListView):

        def get_rows(self, object_list):
            object_list = Solicitacao.objects.filter(
                usuario=recupera_usuario(self.request))
            return [self._as_row(obj) for obj in object_list]

    class CreateView(LoginRequiredMixin, CrudCreateView):
        form_class = SolicitacaoForm

        def get_initial(self):
            try:
                usuario = Usuario.objects.get(user=self.request.user)
                self.initial[u'usuario'] = usuario
                self.initial[u'codigo'] = random.randint(0, 65500)
                self.initial[u'email_contato'] = usuario.email
                self.initial[u'telefone_contato'] = usuario.primeiro_telefone
                self.initial[u'casa_legislativa'] = usuario.casa_legislativa
            except Usuario.DoesNotExist:
                pass
            return self.initial.copy()

        def get_success_url(self):
            return reverse(u'solicitacoes:solicitacao_list')

    class BaseMixin(CrudBaseMixin):
        list_field_names = [u'osticket', u'sistema',
                            u'titulo', u'data_criacao']