from django.shortcuts import get_object_or_404
from sigi.apps.casas.models import Orgao


class ContatoInterlegisViewMixin:
    def get_casa(self):
        user = self.request.user
        if "casa_id" in self.request.session:
            casa_id = int(self.request.session["casa_id"])
            casa = Orgao.objects.filter(id=casa_id).first()
        elif "casa_id" in self.request.GET:
            casa_id = int(self.request.GET["casa_id"])
            casa = Orgao.objects.filter(id=casa_id).first()
        elif user.is_anonymous and hasattr(
            self.get_object(), "casa_legislativa"
        ):
            casa = self.get_object().casa_legislativa
        else:
            casa = Orgao.objects.filter(funcionario__email=user.email).first()
        if casa:
            self.request.session["casa_id"] = casa.id
        return casa

    def get_contato(self):
        if self.request.user.is_anonymous:
            return self.get_casa().contato_interlegis

        return self.get_casa().funcionario_set.get(
            email=self.request.user.email
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["casa"] = self.get_casa()
        return context
