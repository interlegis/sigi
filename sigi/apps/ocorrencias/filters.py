from django.contrib import admin
from django.utils.translation import gettext as _
from sigi.apps.servidores.models import Servidor


class ServidorRegistroFilter(admin.filters.RelatedFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        servidores = Servidor.objects.exclude(ocorrencia=None).order_by(
            "nome_completo"
        )
        self.lookup_choices = [(x.id, x) for x in servidores]
