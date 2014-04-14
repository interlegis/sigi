# -*- coding: utf-8 -*-

from sigi.forms_builder.forms.views import FormDetail, FormSent
from sigi.apps.pesquisas.models import Pesquisa
from sigi.apps.pesquisas.forms import PesquisaForm

class PesquisaDetail(FormDetail):
    form_class = Pesquisa
    form_for_form_class = PesquisaForm
    
class PesquisaSent(FormSent):
    form_class = Pesquisa

form_detail = PesquisaDetail.as_view()
form_sent = PesquisaSent.as_view()