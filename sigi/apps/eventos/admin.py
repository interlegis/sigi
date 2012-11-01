# -*- coding: utf-8 -*-
from django.contrib import admin
from sigi.apps.eventos.models import Recurso

class RecursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade',)
    pass