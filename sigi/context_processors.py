from django.core.exceptions import ObjectDoesNotExist

from sigi.apps.usuarios.models import Usuario


def recupera_usuario(request):

    pk = request.user.pk
    if pk:
        try:
            usuario = Usuario.objects.get(user_id=pk)
        except ObjectDoesNotExist:
            return 0
        else:
            return usuario.pk
    else:
        return 0


def usuario_context(request):
    context = {'usuario_pk': recupera_usuario(request)}
    return context
