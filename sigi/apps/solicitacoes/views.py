from __future__ import absolute_import
import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse

import sigi.apps.crud.base
from sigi.apps.crud.base import Crud, CrudCreateView, CrudListView, CrudCreateView, CrudUpdateView, CrudBaseMixin
from sigi.apps.usuarios.models import Usuario

from .forms import SolicitacaoEditForm, SolicitacaoForm
from .models import Solicitacao


class SolicitacaoCrud(LoginRequiredMixin, Crud):
    model = Solicitacao
    help_path = u''

    class CreateView(LoginRequiredMixin, CrudCreateView):
        form_class = SolicitacaoForm

        def get_initial(self):
            try:
                usuario = Usuario.objects.get(user=self.request.user)
                self.initial[u'usuario'] = usuario
                self.initial[u'codigo'] = random.randint(0, 65500)
                self.initial[u'email_contato'] = usuario.email
                self.initial[u'telefone_contato'] = usuario.primeiro_telefone
            except Usuario.DoesNotExist:
                pass
            return self.initial.copy()

        def get_success_url(self):
            return reverse(u'solicitacoes:solicitacao_list')

    class UpdateView(LoginRequiredMixin, CrudUpdateView):
        form_class = SolicitacaoEditForm

        @property
        def layout_key(self):
            return u'SolicitacaoEdit'

    class ListView(LoginRequiredMixin, CrudListView):
        @property
        def layout_key(self):
            return u'SolicitacaoList'

    class BaseMixin(CrudBaseMixin):
        list_field_names = [u'osticket', u'sistema',
                            u'titulo', u'data_criacao']
