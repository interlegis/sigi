# -*- coding: utf8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from sigi.apps.utils.decorators import login_required
from sigi.apps.diagnosticos.models import Diagnostico, Categoria
from sigi.apps.casas.models import Funcionario
from sigi.apps.diagnosticos.forms import (DiagnosticoMobileForm,
        CasaLegislativaMobileForm, FuncionariosMobileForm)


@cache_page(5)
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


@cache_page(5)
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


@cache_page(5)
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

    if request.method == "POST":
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


@cache_page(5)
@login_required(login_url='/mobile/diagnosticos/login')
def categoria_casa_legislativa(request, id_diagnostico):
    try:
        diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
        casa_legislativa = diagnostico.casa_legislativa
    except Diagnostico.DoesNotExist:
        context = RequestContext(request)
        return render_to_response('mobile/404.html', {})

    if request.method == "POST":
        form = CasaLegislativaMobileForm(request.POST,
            instance=casa_legislativa)
        if form.is_valid():
            form.save()
    else:
        form = CasaLegislativaMobileForm(instance=casa_legislativa)

    context = RequestContext(request, {'form': form,
        'diagnostico': diagnostico, 'casa_legislativa': casa_legislativa})
    return render_to_response(
        'diagnosticos/diagnosticos_categoria_casa_legislativa_form.html',
        context)


@cache_page(5)
@login_required(login_url='/mobile/diagnosticos/login')
def categoria_contatos(request, id_diagnostico):
    try:
        diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
        casa = diagnostico.casa_legislativa
    except Diagnostico.DoesNotExist:
        context = RequestContext(request)
        return render_to_response('mobile/404.html', {})

    funcionarios = [casa.funcionario_set.get_or_create(setor=n)
        for n, l in Funcionario.SETOR_CHOICES]

    if request.method == "POST":
        forms = [FuncionariosMobileForm(
            request.POST, prefix=f.setor, instance=f) for f, c in funcionarios]

        # valida e salva um formulario por vez
        for form in forms:
            if form.is_valid():
                form.save()
    else:
        forms = [FuncionariosMobileForm(prefix=f.setor, instance=f)
            for f, c in funcionarios]

    context = RequestContext(request, {'forms': forms,
        'diagnostico': diagnostico, 'casa_legislativa': casa})
    return render_to_response('diagnosticos/diagnosticos_categoria_contatos_form.html',
        context)
