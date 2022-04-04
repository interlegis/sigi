from django.contrib import admin
from django.utils.translation import gettext as _
from sigi.apps.servidores.models import Servidor


class ServidorRegistroFilter(admin.filters.RelatedFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        servidores = Servidor.objects.exclude(ocorrencia=None).order_by(
            'nome_completo')
        self.lookup_choices = [(x.id, x) for x in servidores]


class OcorrenciaListFilter(admin.SimpleListFilter):
    title = _('Relacionadas a Mim')
    parameter_name = 'minhas'

    def lookups(self, request, model_admin):
        if request.user.servidor is None:
            return None
        return (
            ('M', _('Registrados por mim')),
            ('G', _('Sobre casas que gerencio')),
        )

    def queryset(self, request, queryset):
        servidor = request.user.servidor
        if self.value() == 'M':
            return queryset.filter(servidor_registro=servidor)
        elif self.value() == 'G':
            return queryset.filter(
                casa_legislativa__gerentes_interlegis=servidor
            )
        else:
            return queryset
