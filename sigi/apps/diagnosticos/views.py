# -*- coding: utf8 -*-

from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from sigi.apps.utils.decorators import login_required
from sigi.apps.diagnosticos.decorators import validate_diagnostico
from sigi.apps.diagnosticos.models import Diagnostico, Categoria
from sigi.apps.casas.models import Funcionario
from sigi.apps.servidores.models import Servidor
from sigi.apps.diagnosticos.forms import (DiagnosticoMobileForm,
        CasaLegislativaMobileForm, FuncionariosMobileForm)


@cache_page(5)
@login_required(login_url='/mobile/diagnosticos/login')
def lista(request):
    """Consulta os diagnosticos do servidor logado,
    que contenham o status de não publicado.
    """

    try:
        servidor = request.user.get_profile()
        diagnosticos = servidor.get_diagnosticos(publicado=False)
        context = RequestContext(request, {'diagnosticos': diagnosticos})
        return render_to_response('diagnosticos/diagnosticos_list.html', context)
    except Servidor.DoesNotExist:
        msg = "Para acessar os diagnóstico você precisa ter um servidor cadastrado na sua conta."
        context = RequestContext(request, {'msg': msg})
        return render_to_response('mobile/404.html', context)

@cache_page(5)
@validate_diagnostico
@login_required(login_url='/mobile/diagnosticos/login')
def categorias(request, id_diagnostico):
    """Consulta as categorias do diagnostico selecionado
    a partir da sua identificação
    """
    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    categorias = Categoria.objects.all()

    context = RequestContext(request, {'categorias': categorias,
        'diagnostico': id_diagnostico})
    return render_to_response('diagnosticos/diagnosticos_categorias_list.html',
        context)


@cache_page(5)
@validate_diagnostico
@login_required(login_url='/mobile/diagnosticos/login')
def categoria_detalhes(request, id_diagnostico, id_categoria):
    """Captura as perguntas da categoria
    selecionada. Durante o preenchimento das perguntas, o camada
    template do projeto, vai requisitar a inserção dos campos via
    AJAX a cada mudança de pergunta

    Caso alguma inserção não passe na validação do formulário em
    questão, será enviado as mensagens de erro no formato JSON,
    para que a camada de template do projeto trate-as de forma adequada.
    """

    try:
        categoria = Categoria.objects.get(pk=id_categoria)
    except Categoria.DoesNotExist:
        context = RequestContext(request)
        return render_to_response('mobile/404.html', {})

    diagnostico = Diagnostico.objects.filter(status=False).get(pk=id_diagnostico)

    if request.method == "POST":
        form = DiagnosticoMobileForm(request.POST,
            instance=diagnostico, category=id_categoria)
        if form.is_valid():
            form.save()
        else:
            erros = []
            for field in form:
                if field.errors:
                    campo = field.name
                    erros.append(field.errors)
            resposta = {
                'mensagem': 'erro',
                'campo': campo,
                'erros': erros
            }
            json = simplejson.dumps(resposta)
            print json
            return HttpResponse(json, mimetype="application/json")
    else:
        form = DiagnosticoMobileForm(instance=diagnostico,
            category=id_categoria)

    context = RequestContext(request, {'form': form, 'categoria': categoria,
        'diagnostico': diagnostico})
    return render_to_response('diagnosticos/diagnosticos_categorias_form.html',
        context)


@cache_page(5)
@validate_diagnostico
@login_required(login_url='/mobile/diagnosticos/login')
def categoria_casa_legislativa(request, id_diagnostico):

    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    casa_legislativa = diagnostico.casa_legislativa

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
@validate_diagnostico
@login_required(login_url='/mobile/diagnosticos/login')
def categoria_contatos(request, id_diagnostico):

    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    casa_legislativa = diagnostico.casa_legislativa

    funcionarios = [casa_legislativa.funcionario_set.get_or_create(setor=n)
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
        'diagnostico': diagnostico, 'casa_legislativa': casa_legislativa})
    return render_to_response('diagnosticos/diagnosticos_categoria_contatos_form.html',
        context)
