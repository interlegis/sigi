# -*- coding: utf8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from sigi.apps.utils.decorators import login_required
from sigi.apps.diagnosticos.models import Diagnostico, Categoria
from sigi.apps.diagnosticos.forms import DiagnosticoMobileForm


@login_required(login_url='/mobile/diagnosticos/login')
def lista(request):
    """Consulta os diagnosticos do servidor logado,
    que contenham o status de não publicado.
    """

    # TODO Implementar pesquisa de diagnosticos, em que esses registros
    # devem ser criado pelo servidor logado.
    diagnosticos = Diagnostico.objects.filter(status=False).filter(
        responsavel=request.user.get_profile())

    context = RequestContext(request, {'diagnosticos': diagnosticos})
    return render_to_response('diagnosticos/diagnosticos_list.html', context)


@login_required(login_url='/mobile/diagnosticos/login')
def categorias(request, id_diagnostico):
    """Consulta as categorias do diagnostico selecionado
    a partir da sua identificação
    """
    categorias = Categoria.objects.all()

    context = RequestContext(request, {'categorias': categorias,
        'diagnostico': id_diagnostico})
    return render_to_response('diagnosticos/diagnosticos_categorias_list.html',
        context)


@login_required(login_url='/mobile/diagnosticos/login')
def categoria_detalhes(request, id_diagnostico, id_categoria):
    """Captura as perguntas da categoria
    selecionada.
    """
    try:
        diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
        categoria = Categoria.objects.get(pk=id_categoria)
    except Diagnostico.DoesNotExist, Categoria.DoesNotExist:
        context = RequestContext(request)
        return render_to_response('mobile/404.html', {})

    if request.POST:
        form = DiagnosticoMobileForm(request.POST,
            instance=diagnostico, category=id_categoria)
        if form.is_valid():
            form.save()
    else:
        form = DiagnosticoMobileForm(instance=diagnostico,
            category=id_categoria)

    context = RequestContext(request, {'form': form, 'categoria': categoria,
        'diagnostico': diagnostico})
    return render_to_response('diagnosticos/diagnosticos_categorias_form.html',
        context)
