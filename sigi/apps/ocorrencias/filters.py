from django.contrib import admin
from django.utils.translation import gettext as _

from sigi.apps.servidores.models import Servidor


class OcorrenciaListFilter(admin.SimpleListFilter):
    title = _('Relacionadas a Mim')
    parameter_name = 'minhas'

    def lookups(self, request, model_admin):
        if request.user.servidor is None:
            return None
        return (
            ('S', _('Atribuídos ao meu setor')),
            ('M', _('Registrados por mim')),
            ('G', _('Sobre casas que gerencio')),
        )

    def queryset(self, request, queryset):
        servidor = request.user.servidor
        if self.value() == 'S':
            return queryset.filter(setor_responsavel=servidor.servico)
        elif self.value() == 'M':
            return queryset.filter(servidor_registro=servidor)
        elif self.value() == 'G':
            return queryset.filter(
                casa_legislativa__gerentes_interlegis=servidor
            )
        else:
            return queryset
