from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.serializers import serialize
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_list_or_404
from django.template import Context, loader, RequestContext
from django.views.decorators.csrf import csrf_protect
from sigi.apps.casas.models import Orgao
from sigi.apps.parlamentares.models import Parlamentar


def parlamentares_casa(request, casa_id):
    return JsonResponse(
        {
            p.nome_completo: {
                "foto": p.foto.url if p.foto else None,
                "id": p.id,
            }
            for p in Parlamentar.objects.filter(casa_legislativa_id=casa_id)
        }
    )


def parlamentar_data(request):
    return HttpResponse(
        serialize(
            "json", Parlamentar.objects.filter(id=request.GET.get("id", None))
        ),
        content_type="application/json",
    )
