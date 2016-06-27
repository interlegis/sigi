# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _

from sigi.apps.saberes.models import CategoriasInteresse


class CategoriasInteresseAdmin(admin.ModelAdmin):
    list_display = ('prefixo', 'descricao', 'count_categorias',)

    def count_categorias(self, obj):
        return obj.categorias().count()
    count_categorias.short_description = _("Categorias que casam")
admin.site.register(CategoriasInteresse, CategoriasInteresseAdmin)
