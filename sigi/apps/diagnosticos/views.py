# -*- coding: utf8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

from sigi.apps.diagnosticos.models import Diagnostico


def lista(request):
    """Consulta os diagnosticos do servidor logado,
    que contenham o status de não publicado.
    """

    # TODO Implementar pesquisa de diagnosticos, em que esses registros
    # devem ser criado pelo servidor logado.
    diagnosticos = Diagnostico.objects.all()

    context = RequestContext(request, {'diagnosticos': diagnosticos})
    return render_to_response('diagnosticos/diagnosticos_list.html', context)
