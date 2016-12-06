# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

from sigi.apps.diagnosticos.models import Diagnostico


def validate_diagnostico(func):
    def decorator(request, id_diagnostico, *args, **kwargs):
        """ Retorna 404 caso o diagnostico esteja publicado
        ou o usuario nao seja um membro da equipe
        """
        try:
            diagnostico = Diagnostico.objects.filter(publicado=False).get(pk=id_diagnostico)
            if (request.user.servidor in diagnostico.membros):
                # continua o processamento normal da view
                return func(request, id_diagnostico, *args, **kwargs)
        except Diagnostico.DoesNotExist:
            pass

        # renderiza a pagina de 404
        context = RequestContext(request, {})
        return render_to_response('mobile/404.html', context)
    return decorator
