from django.contrib.admin.sites import site
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView
from sigi.apps.casas.models import Orgao
from sigi.apps.parlamentares.forms import ParlamentarForm
from sigi.apps.parlamentares.models import Parlamentar


def parlamentares_casa(request, casa_id):
    return JsonResponse(
        {
            p.nome_completo: {
                "foto": p.foto.url if p.foto else None,
                "id": p.id,
            }
            for p in Parlamentar.objects.filter(casa_legislativa_id=casa_id)
        }
    )


def parlamentar_data(request):
    return HttpResponse(
        serialize(
            "json", Parlamentar.objects.filter(id=request.GET.get("id", None))
        ),
        content_type="application/json",
    )


################################################################################
# Views para site público - acesso dos contatos Interlegis                     #
################################################################################


class ParlamentarListView(LoginRequiredMixin, ListView):
    model = Parlamentar
    paginate_by = 100
    template_name = "public/parlamentar_list.html"

    def get_object(self):
        casa_id = self.request.session.get("casa_id", None)
        if casa_id:
            casa = Orgao.objects.filter(id=casa_id).first()
        else:
            casa = Orgao.objects.filter(
                funcionario__email=self.request.user.email
            ).first()
        return casa

    def get_queryset(self):
        casa = self.get_object()
        if casa:
            if self.request.GET.get("suplentes", 0):
                return casa.parlamentar_set.all()
            else:
                return casa.parlamentar_set.exclude(status_mandato="S")
        else:
            return Parlamentar.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["casa"] = self.get_object()
        if self.request.GET.get("suplentes", 0):
            context["suplentes"] = True
        return context


class ParlamentarUpdateView(LoginRequiredMixin, UpdateView):
    model = Parlamentar
    form_class = ParlamentarForm
    template_name = "public/parlamentar_update.html"
    success_url = reverse_lazy("parlamentares:parlamentar_listview")

    def get_casa(self):
        casa_id = self.request.session.get("casa_id", None)
        if casa_id:
            casa = Orgao.objects.filter(id=casa_id).first()
        else:
            casa = Orgao.objects.filter(
                funcionario__email=self.request.user.email
            ).first()
        return casa

    def get_object(self, queryset=None):
        casa = self.get_casa()
        return super().get_object(casa.parlamentar_set.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["casa"] = self.get_casa()
        return context
