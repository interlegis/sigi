# coding: utf-8
from django.views.generic.base import TemplateView
from django.db.models import Count

from sigi.apps.pesquisas.models import Pesquisa, Pergunta, Resposta
from sigi.apps.pesquisas.forms import PesquisaForm

from forms_builder.forms.views import FormDetail, FormSent


class PesquisaDetail(FormDetail):
    form_class = Pesquisa
    form_for_form_class = PesquisaForm


class PesquisaSent(FormSent):
    form_class = Pesquisa

form_detail = PesquisaDetail.as_view()
form_sent = PesquisaSent.as_view()


class ChartView(TemplateView):
    template_name = 'pesquisas/chart.html'

    def get_context_data(self, **kwargs):
        context = super(ChartView, self).get_context_data(**kwargs)
        field_id = self.kwargs['field_id']
        context['label'] = Pergunta.objects.filter(id=field_id)
        dados = Resposta.objects.filter(field_id=field_id).values('value').annotate(total=Count('value'))
        context['dados'] = dados
        context['field_id'] = field_id
        return context

chart_view = ChartView.as_view()