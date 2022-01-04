# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import gettext as _

from sigi.apps.servidores.models import Servidor


class OcorrenciaListFilter(admin.SimpleListFilter):

    title = _(u'Relacionadas a Mim')
    parameter_name = 'minhas'

    def lookups(self, request, model_admin):
        if request.user.servidor is None:
            return None
        return (
            ('S', _(u'Atribuídos ao meu setor')),
            ('M', _(u'Registrados por mim')),
            ('G', _(u'Sobre casas que gerencio')),
        )

    def queryset(self, request, queryset):
        servidor = request.user.servidor
        # servidor = Servidor.objects.get(user=request.user)
        if self.value() == 'S':
            return queryset.filter(setor_responsavel=servidor.servico)
        elif self.value() == 'M':
            return queryset.filter(servidor_registro=servidor)
        elif self.value() == 'G':
            return queryset.filter(
                casa_legislativa__gerentes_interlegis=servidor
            )
