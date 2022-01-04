# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import gettext as _

from sigi.apps.metas.models import PlanoDiretor
from sigi.apps.utils.base_admin import BaseModelAdmin


class MetaAdmin(BaseModelAdmin):
    list_display = ('projeto', 'titulo', 'data_inicio', 'data_fim', 'valor_meta', 'valor_executado', 'percentual_concluido',)
    fields = ('projeto', 'titulo', 'descricao', 'data_inicio', 'data_fim', 'algoritmo', 'valor_meta',)
    list_filter = ('projeto',)


class PlanoDiretorAdmin(BaseModelAdmin):
    list_display = ('projeto', 'casa_legislativa', 'get_uf', 'status', 'data_entrega', 'data_implantacao',)
    fields = ('projeto', 'casa_legislativa', 'status', 'data_entrega', 'data_implantacao',)
    raw_id_fields = ('casa_legislativa',)
    list_filter = ('projeto', 'status', 'casa_legislativa', 'casa_legislativa__municipio__uf__nome')

    def get_uf(self, obj):
        return obj.casa_legislativa.municipio.uf.nome
    get_uf.short_description = _("UF")
    get_uf.admin_order_field = 'casa_legislativa__municipio__uf__nome'

    def lookup_allowed(self, lookup, value):
        return super(PlanoDiretorAdmin, self).lookup_allowed(lookup, value) or \
            lookup in ['casa_legislativa__municipio__uf__codigo_ibge__exact']

    def changelist_view(self, request, extra_context=None):
        import re
        request.GET._mutable = True
        if 'data_entrega__gte' in request.GET:
            value = request.GET.get('data_entrega__gte', '')
            if value == '':
                del request.GET['data_entrega__gte']
            elif re.match('^\d*$', value):  # Year only
                request.GET['data_entrega__gte'] = "%s-01-01" % value  # Complete with january 1st
            elif re.match('^\d*\D\d*$', value):  # Year and month
                request.GET['data_entrega__gte'] = '%s-01' % value  # Complete with 1st day of month
        if 'data_entrega__lte' in request.GET:
            value = request.GET.get('data_entrega__lte', '')
            if value == '':
                del request.GET['data_entrega__lte']
            elif re.match('^\d*$', value):  # Year only
                request.GET['data_entrega__lte'] = "%s-01-01" % value  # Complete with january 1st
            elif re.match('^\d*\D\d*$', value):  # Year and month
                request.GET['data_entrega__lte'] = '%s-01' % value  # Complete with 1st day of month
        request.GET._mutable = False

        return super(PlanoDiretorAdmin, self).changelist_view(request, extra_context)

admin.site.register(PlanoDiretor, PlanoDiretorAdmin)
