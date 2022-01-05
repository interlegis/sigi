from django.contrib import admin
from django.utils.translation import gettext as _
from sigi.apps.servidores.models import Servico


class ServicoFilter(admin.SimpleListFilter):
    title = _("Subordinados à")
    parameter_name = 'subordinado__id__exact'

    def lookups(self, request, model_admin):
        return ([('None', _("Nenhum"))] +
                [(s.id, s.nome) for s in Servico.objects.exclude(servico=None)])

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "None":
                queryset = queryset.filter(subordinado=None)
            else:
                queryset = queryset.filter(subordinado__id=self.value())
        return queryset
