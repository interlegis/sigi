# -*- coding: utf8 -*-

from sigi.apps.diagnosticos.models import Diagnostico
from sigi.apps.servidores.models import Servidor

def validate_diagnostico(func):
    def decorator(request, id_diagnostico, *args, **kwargs):
        """ Retorna 404 caso o diagnostico esteja publicado
        ou o usuario nao seja um membro da equipe
        """
        msg = None
        try:
            diagnostico = Diagnostico.objects.filter(status=False).get(pk=id_diagnostico)
            if (request.user.get_profile() in diagnostico.get_membros()):
                # continua o processamento normal da view
                return func(request, id_diagnostico, *args, **kwargs)
        except Servidor.DoesNotExist:
            msg = "Para acessar os diagnóstico você precisa ter um servidor cadastrado na sua conta."
        except Diagnostico.DoesNotExist:
            pass

        # renderiza a pagina de 404
        context = RequestContext(request, {'msg': msg})
        return render_to_response('mobile/404.html', context)
    return decorator
