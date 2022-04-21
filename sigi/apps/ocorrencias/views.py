# -*- coding: utf-8 -*-
from django.http import JsonResponse, Http404
from django.db.models import Q, Count
from django.utils.translation import ngettext, gettext as _
from django.shortcuts import get_object_or_404, render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.template import RequestContext
from sigi.apps.utils import to_ascii
from sigi.apps.casas.models import Orgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.servidores.models import Servidor, Servico
from sigi.apps.ocorrencias.models import Ocorrencia, Anexo
from sigi.apps.ocorrencias.forms import (
    AnexoForm,
    ComentarioForm,
    OcorrenciaForm,
)
from django.utils.html import escape


@login_required
def painel_ocorrencias(request):
    painel = request.GET.get("painel", None)
    id_servidor = request.GET.get("servidor", None)
    id_casa = request.GET.get("casa", None)
    page = int(request.GET.get("page", "0"))

    paineis = {
        "gerente": _("Casas que gerencio"),
        "registro": _("Ocorrências registrados por mim"),
        "tudo": _("Todas as ocorrências"),
    }

    if id_servidor is None:
        servidor = request.user.servidor
    else:
        servidor = get_object_or_404(Servidor, id=id_servidor)

    if id_casa is not None:
        casa = get_object_or_404(Orgao, id=id_casa)
        painel = "tudo"
        panel_title = _(f"Ocorrências da {casa.nome}, {casa.municipio.uf.nome}")
    else:
        casa = None
        if servidor:
            is_gerente = servidor.casas_que_gerencia.exists()
            is_registrador = (
                servidor.ocorrencia_set.exists()
                or servidor.comentario_set.exists()
            )
            panel_title = servidor.nome_completo
        else:
            is_gerente = False
            is_registrador = False
            panel_title = _("Todas as ocorrências")

        if (servidor is None) or (not is_gerente and not is_registrador):
            painel = "tudo"
        elif not is_gerente and is_registrador:
            painel = "registro"
        elif is_gerente:
            if painel is None:
                painel = "gerente"

    if painel == "gerente":
        ocorrencias = Ocorrencia.objects.filter(
            casa_legislativa__gerentes_interlegis=servidor
        )
    elif painel == "registro":
        ocorrencias = Ocorrencia.objects.filter(
            servidor_registro=servidor
        ) | Ocorrencia.objects.filter(comentarios__usuario=servidor)
    else:  # Tudo...
        if casa is None:  # ...de todas as Casas...
            ocorrencias = Ocorrencia.objects.all()
        else:  # ... ou da Casa escolhida
            ocorrencias = casa.ocorrencia_set.all()

    ocorrencias = ocorrencias.filter(status__in=[1, 2])
    ocorrencias = ocorrencias.order_by("prioridade", "-data_modificacao")
    ocorrencias = ocorrencias.select_related(
        "casa_legislativa",
        "casa_legislativa__municipio",
        "casa_legislativa__municipio__uf",
        "categoria",
        "tipo_contato",
        "servidor_registro",
    )
    ocorrencias = ocorrencias.prefetch_related(
        "comentarios",
        "comentarios__usuario",
        "anexo_set",
        "casa_legislativa__gerentes_interlegis",
    )
    ocorrencias = ocorrencias.annotate(total_anexos=Count("anexo"))

    if page * 100 > ocorrencias.count():
        ocorrencias = ocorrencias[-100]
    else:
        ocorrencias = ocorrencias[page * 100 : page * 100 + 100]

    context = {
        "paineis": paineis,
        "painel": painel,
        "servidor": servidor,
        "casa": casa,
        "ocorrencias": ocorrencias,
        "panel_title": panel_title,
        "comentario_form": ComentarioForm(),
        "ocorrencia_form": OcorrenciaForm(),
        "PRIORITY_CHOICES": Ocorrencia.PRIORITY_CHOICES,
    }

    return render(request, "ocorrencias/painel.html", context)


@login_required
def busca_nominal(request, origin="tudo"):
    term = request.GET.get("term", None)
    if term is None:
        return JsonResponse(
            [{"label": _("Erro na pesquisa por termo"), "value": "type=error"}],
            safe=False,
        )

    data = []

    if origin == "casa" or origin == "tudo":
        casas = Orgao.objects.filter(
            search_text__icontains=to_ascii(term)
        ).select_related("municipio", "municipio__uf")[:10]
        data += [
            {
                "value": c.pk,
                "label": "%s, %s"
                % (
                    c.nome,
                    c.municipio.uf.sigla,
                ),
                "origin": "casa",
            }
            for c in casas
        ]

    if origin == "servidor" or origin == "tudo":
        servidores = Servidor.objects.filter(nome_completo__icontains=term)[:10]
        data += [
            {"value": s.pk, "label": s.nome_completo, "origin": "servidor"}
            for s in servidores
        ]

    if origin == "servico" or origin == "tudo":
        setores = Servico.objects.filter(
            nome__icontains=term
        ) | Servico.objects.filter(sigla__icontains=term)
        setores = setores[:10]
        data += [
            {
                "value": s.pk,
                "label": "%s - %s" % (s.sigla, s.nome),
                "origin": "servico",
            }
            for s in setores
        ]

    data = sorted(data, key=lambda d: d["label"])

    return JsonResponse(data, safe=False)


@login_required
@require_POST
def muda_prioridade(request):
    id_ocorrencia = request.POST.get("id_ocorrencia", None)
    prioridade = request.POST.get("prioridade", None)

    if id_ocorrencia is None or prioridade is None:
        return JsonResponse(
            {"result": "error", "message": _("Erro nos parâmetros")}
        )

    if not any([int(prioridade) == p[0] for p in Ocorrencia.PRIORITY_CHOICES]):
        return JsonResponse(
            {"result": "error", "message": _("Valor de prioridade não aceito")}
        )

    try:
        ocorrencia = Ocorrencia.objects.get(pk=id_ocorrencia)
    except Exception as e:
        return JsonResponse({"result": "error", "message": str(e)})

    ocorrencia.prioridade = prioridade
    ocorrencia.save()

    return JsonResponse(
        {"result": "success", "message": _("Prioridade alterada")}
    )


@login_required
def exclui_anexo(request):
    anexo_id = request.GET.get("anexo_id", None)

    if anexo_id is None:
        return JsonResponse(
            {"result": "error", "message": _("Erro nos parâmetros")}
        )

    try:
        anexo = Anexo.objects.get(pk=anexo_id)
    except Exception as e:
        return JsonResponse({"result": "error", "message": str(e)})

    ocorrencia = anexo.ocorrencia
    anexo.delete()

    link_label = ngettext(
        "%s arquivo anexo", "%s arquivos anexos", ocorrencia.anexo_set.count()
    ) % (ocorrencia.anexo_set.count(),)

    painel = render_to_string(
        "ocorrencias/anexos_snippet.html",
        {"ocorrencia": ocorrencia},
        context_instance=RequestContext(request),
    )

    return JsonResponse(
        {
            "result": "success",
            "message": _("Anexo %s excluído com sucesso" % (anexo_id,)),
            "link_label": link_label,
            "anexos_panel": painel,
        }
    )


@login_required
def inclui_anexo(request):
    if request.method == "POST":
        form = AnexoForm(request.POST, request.FILES)
        if form.is_valid():
            anexo = form.save()
            return HttpResponse(
                '<script type="text/javascript">opener.dismissAddAnexoPopup(window, "%s");</script>'
                % escape(anexo.ocorrencia_id)
            )
        else:
            ocorrencia = form.instance.ocorrencia
    else:
        ocorrencia_id = request.GET.get("ocorrencia_id", None)
        ocorrencia = get_object_or_404(Ocorrencia, pk=ocorrencia_id)
        form = AnexoForm(instance=Anexo(ocorrencia=ocorrencia))
    return render(
        request,
        "ocorrencias/anexo_form.html",
        {"form": form, "ocorrencia": ocorrencia, "is_popup": True},
    )


@login_required
def anexo_snippet(request):
    ocorrencia_id = request.GET.get("ocorrencia_id", None)
    ocorrencia = get_object_or_404(Ocorrencia, pk=ocorrencia_id)
    return render(
        request, "ocorrencias/anexos_snippet.html", {"ocorrencia": ocorrencia}
    )


@login_required
@require_POST
def inclui_comentario(request):
    form = ComentarioForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.usuario = Servidor.objects.get(user=request.user)
        comentario.save()
        ocorrencia = comentario.ocorrencia
        form = ComentarioForm()
    else:
        ocorrencia = form.instance.ocorrencia

    painel = render_to_string(
        "ocorrencias/ocorrencia_snippet.html",
        {
            "ocorrencia": ocorrencia,
            "comentario_form": form,
        },
        context_instance=RequestContext(request),
    )

    return JsonResponse(
        {"ocorrencia_id": ocorrencia.id, "ocorrencia_panel": painel}
    )


@login_required
@require_POST
def inclui_ocorrencia(request):
    form = OcorrenciaForm(request.POST)

    data = {}

    if form.is_valid():
        ocorrencia = form.save(commit=False)
        ocorrencia.servidor_registro = Servidor.objects.get(user=request.user)
        ocorrencia.save()
        form = OcorrenciaForm()
        data["result"] = "success"
        data["ocorrencia_panel"] = render_to_string(
            "ocorrencias/ocorrencia_snippet.html",
            {
                "ocorrencia": ocorrencia,
                "comentario_form": ComentarioForm(),
                "PRIORITY_CHOICES": Ocorrencia.PRIORITY_CHOICES,
            },
            context_instance=RequestContext(request),
        )
    else:
        data["result"] = "error"

    data["ocorrencia_form"] = render_to_string(
        "ocorrencias/ocorrencia_form.html",
        {"ocorrencia_form": form},
        context_instance=RequestContext(request),
    )

    return JsonResponse(data)
