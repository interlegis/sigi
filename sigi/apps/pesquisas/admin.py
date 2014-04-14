# -*- coding: utf-8 -*-

from django.contrib import admin
from sigi.forms_builder.forms.admin import FieldAdmin, FormAdmin
from sigi.apps.pesquisas.models import Pesquisa, Pergunta, Formulario, Resposta

class PerguntaAdmin(FieldAdmin):
    model = Pergunta

class PesquisaAdmin(FormAdmin):
    formentry_model = Formulario
    fieldentry_model = Resposta
    inlines = (PerguntaAdmin,)
    
admin.site.register(Pesquisa, PesquisaAdmin)