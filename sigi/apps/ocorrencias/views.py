import copy
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.admin.sites import site
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.template.loader import render_to_string
from django.template import RequestContext
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ngettext, gettext as _
from django.views.decorators.http import require_POST
from sigi.apps import ocorrencias
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.utils import to_ascii
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.servidores.models import Servidor, Servico
from sigi.apps.ocorrencias.models import (
    Categoria,
    Comentario,
    Ocorrencia,
    Anexo,
    TipoContato,
)
from sigi.apps.ocorrencias.forms import (
    AnexoForm,
    ComentarioForm,
    ComentarioInternoForm,
    ContatoForm,
    DocumentoForm,
    OcorrenciaChangeForm,
    OcorrenciaForm,
    CasaForm,
    PresidenteForm,
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


def seleciona_casa(request):
    context = site.each_context(request) or {}
    casa_id = request.GET.get("casa_id", None)

    if casa_id:
        casa = get_object_or_404(Orgao, pk=casa_id)
        categoria = get_object_or_404(Categoria, tipo="C")
        tipo_contato = get_object_or_404(TipoContato, ind_site=True)

        if request.user.is_anonymous or not (
            request.user.is_staff and request.user.servidor is not None
        ):
            servidor = get_object_or_404(Servidor, sigi=True)
        else:
            servidor = request.user.servidor

        if casa.convenio_set.filter(projeto__sigla="ACT").exists():
            # TODO: Fluxo para Casa já conveniada
            messages.info(request, "Já conveniada")
            return redirect("/")
        ocorrencia = casa.ocorrencia_set.filter(
            categoria=categoria,
            status__in=[Ocorrencia.STATUS_ABERTO, Ocorrencia.STATUS_REABERTO],
        ).first()
        if not ocorrencia:
            ocorrencia = Ocorrencia(
                casa_legislativa=casa,
                categoria=categoria,
                tipo_contato=tipo_contato,
                assunto=_("Solicitação de Adesão ao Programa Interlegis"),
                descricao=_(
                    f"A {casa.nome} solicita adesão ao Programa Interlegis"
                ),
                servidor_registro=servidor,
            )
            ocorrencia.save()
        return redirect(reverse("ocorrencias_ocorrencia", args=[ocorrencia.id]))

    return render(request, "ocorrencias/convenio/seleciona_casa.html", context)


def bound_copy(instance, bound_data, removes=None):
    data = bound_data.copy()
    if removes:
        for remove_key in removes:
            data.pop(remove_key)
    for key, value in data.items():
        setattr(instance, key, value)


def ocorrencia(request, ocorrencia_id):
    ANEXO_DESCRICAO = _("Solicitação de convenio assinada")

    def set_instances():
        if ocorrencia.casa_foto:
            casa.foto = ocorrencia.casa_foto
        if ocorrencia.casa_brasao:
            casa.brasao = ocorrencia.casa_brasao
        if "casa_legislativa" in infos:
            bound_copy(casa, infos["casa_legislativa"])
        if "presidente" in infos:
            bound_copy(presidente, infos["presidente"], ["id"])
        if "contato" in infos:
            bound_copy(contato, infos["contato"])

    ocorrencia = get_object_or_404(Ocorrencia, pk=ocorrencia_id)
    infos = ocorrencia.infos or {}
    casa = ocorrencia.casa_legislativa
    presidente = casa.presidente or (
        Parlamentar.objects.get(id=infos["presidente"]["id"])
        if "presidente" in infos
        else Parlamentar(casa_legislativa=casa)
    )
    contato = casa.contato_interlegis or Funcionario(
        casa_legislativa=casa, setor="contato_interlegis"
    )
    documento = (
        ocorrencia.anexo_set.get(id=infos["documento"]["id"])
        if "documento" in infos
        else Anexo(ocorrencia=ocorrencia, descricao=ANEXO_DESCRICAO)
    )

    set_instances()

    contato_form = ContatoForm(instance=contato, prefix="contato")
    documento_form = DocumentoForm(instance=documento)

    if request.method == "POST":
        if "salva_casa" in request.POST:
            casa_form = CasaForm(
                request.POST, request.FILES, instance=casa, prefix="casa"
            )
            if casa_form.is_valid():
                cleaned = casa_form.cleaned_data.copy()
                foto = cleaned.pop("foto")
                brasao = cleaned.pop("brasao")
                if "foto" in casa_form.changed_data:
                    if foto == False:
                        if ocorrencia.casa_foto:
                            ocorrencia.casa_foto.delete(save=True)
                    else:
                        ocorrencia.casa_foto = foto
                if "brasao" in casa_form.changed_data:
                    if brasao == False:
                        if ocorrencia.casa_brasao:
                            ocorrencia.casa_brasao.delete(save=True)
                    else:
                        ocorrencia.casa_brasao = brasao

                infos["casa_legislativa"] = cleaned
                ocorrencia.infos = infos
                ocorrencia.save()
            else:
                messages.error(
                    request,
                    _("Corrija os erros no cadastro da Casa Legislativa"),
                )
        elif "salva_presidente" in request.POST:
            presidente_form = PresidenteForm(
                request.POST, instance=presidente, prefix="presidente"
            )
            if presidente_form.is_valid():
                cleaned = presidente_form.cleaned_data.copy()
                presidente = cleaned.pop("parlamentar")
                cleaned["id"] = presidente.id
                infos["presidente"] = cleaned
                ocorrencia.infos = infos
                ocorrencia.save()
        elif "salva_contato" in request.POST:
            contato_form = ContatoForm(
                request.POST, instance=contato, prefix="contato"
            )
            if contato_form.is_valid():
                infos["contato"] = contato_form.cleaned_data.copy()
                ocorrencia.infos = infos
                ocorrencia.save()
        elif "salva_documento" in request.POST:
            documento_form = DocumentoForm(
                request.POST, request.FILES, instance=documento
            )
            if documento_form.is_valid():
                documento = documento_form.save()
                infos["documento"] = {"id": documento.id}
                ocorrencia.infos = infos
                ocorrencia.save()
        elif "salva_comentario" in request.POST:
            comentario_form = ComentarioForm(request.POST)
            if comentario_form.is_valid():
                comentario = comentario_form.save(commit=False)
                comentario.ocorrencia = ocorrencia
                comentario.usuario = ocorrencia.servidor_registro
                if ocorrencia.status not in [
                    ocorrencia.STATUS_ABERTO,
                    ocorrencia.STATUS_REABERTO,
                ]:
                    comentario.novo_status = ocorrencia.STATUS_REABERTO
                comentario.save()

        set_instances()

        if {"casa_legislativa", "presidente", "contato"}.issubset(
            infos
        ) and "documento" not in infos:
            ocorrencia.anexo_set.all().delete()
            documento = Anexo(ocorrencia=ocorrencia, descricao=ANEXO_DESCRICAO)
            documento_form = DocumentoForm(instance=documento)
            projeto = ocorrencia.categoria.projeto
            oficio = Anexo(
                ocorrencia=ocorrencia,
                descricao=f"Solicitação de {projeto.sigla}",
            )
            oficio.arquivo.name = (
                f"{Anexo.arquivo.field.upload_to}/"
                f"solicitacao_{projeto.sigla}_{casa.get_sigla()}.pdf"
            )
            projeto.gerar_oficio(
                oficio.arquivo,
                casa,
                presidente,
                contato,
                request.build_absolute_uri("/"),
            )
            oficio.save()
            minuta = Anexo(
                ocorrencia=ocorrencia, descricao=f"Minuta de {projeto.sigla}"
            )
            minuta.arquivo.name = (
                f"{Anexo.arquivo.field.upload_to}/"
                f"minuta_{projeto.sigla}_{casa.get_sigla()}.docx"
            )
            projeto.gerar_minuta(minuta.arquivo.path, casa, presidente, contato)
            minuta.save()

    if presidente.id:
        bounds = {
            f"presidente-{key}": value
            for key, value in infos["presidente"].items()
            if key != "id"
        }
        bounds["presidente-parlamentar"] = presidente
        presidente_form = PresidenteForm(
            bounds, instance=presidente, prefix="presidente"
        )
    else:
        presidente_form = PresidenteForm(
            instance=presidente, prefix="presidente"
        )

    context = site.each_context(request) or {}
    context.update(
        {
            "ocorrencia": ocorrencia,
            "casa_form": CasaForm(instance=casa, prefix="casa"),
            "presidente_form": presidente_form,
            "contato_form": contato_form,
            "documento_form": documento_form,
            "comentario_form": ComentarioForm(),
            "infos": infos,
        }
    )
    return render(request, "ocorrencias/convenio/ocorrencia.html", context)


@login_required
def painel_convenio(request, ocorrencia_id=None):
    context = site.each_context(request) or {}

    if ocorrencia_id:
        ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id)

        if request.method == "POST":
            if "salva_ocorrencia" in request.POST:
                ocorrencia_form = OcorrenciaChangeForm(
                    request.POST, instance=ocorrencia
                )
                if ocorrencia_form.is_valid():
                    ocorrencia = ocorrencia_form.save()
                    if "processo_sigad" in ocorrencia_form.changed_data:
                        Comentario(
                            ocorrencia=ocorrencia,
                            descricao=_(
                                f"criado processo administrativo nº {ocorrencia.processo_sigad}"
                            ),
                            usuario=request.user.servidor,
                        ).save()

            if "salva_comentario" in request.POST:
                comentario_form = ComentarioInternoForm(request.POST)
                if comentario_form.is_valid():
                    comentario = comentario_form.save(commit=False)
                    comentario.ocorrencia = ocorrencia
                    comentario.usuario = request.user.servidor
                    comentario.save()

        casa = ocorrencia.casa_legislativa
        novo_presidente = (
            get_object_or_404(
                Parlamentar, id=ocorrencia.infos["presidente"]["id"]
            )
            if ocorrencia.infos["presidente"]
            else None
        )
        contato = casa.contato_interlegis or Funcionario()

        if not "aplicados" in ocorrencia.infos:
            ocorrencia.infos["aplicados"] = []

        apply = request.GET.get("apply", None)

        if (
            apply == "casa"
            and "casa_legislativa" in ocorrencia.infos
            and not "casa_legislativa" in ocorrencia.infos["aplicados"]
        ):
            if ocorrencia.casa_foto:
                casa.foto = ocorrencia.casa_foto
            if ocorrencia.casa_brasao:
                casa.brasao = ocorrencia.casa_brasao
            bound_copy(casa, ocorrencia.infos["casa_legislativa"])
            casa.save()
            ocorrencia.infos["aplicados"].append("casa_legislativa")
            ocorrencia.save()

        if (
            apply == "presidente"
            and "presidente" in ocorrencia.infos
            and "presidente" not in ocorrencia.infos["aplicados"]
        ):
            bound_copy(novo_presidente, ocorrencia.infos["presidente"], ["id"])
            novo_presidente.save()
            ocorrencia.infos["aplicados"].append("presidente")
            ocorrencia.save()

        if (
            apply == "contato"
            and "contato" in ocorrencia.infos
            and "contato" not in ocorrencia.infos["aplicados"]
        ):
            bound_copy(contato, ocorrencia.infos["contato"])
            contato.save()
            ocorrencia.infos["aplicados"].append("contato")
            ocorrencia.save()

        infos = copy.deepcopy(ocorrencia.infos)

        if infos["presidente"]:
            del infos["presidente"]["id"]

        context.update(
            {
                "ocorrencia": ocorrencia,
                "campos_ocorrencia": [
                    "assunto",
                    "casa_legislativa",
                    "categoria",
                    "descricao",
                    "data_criacao",
                    "data_modificacao",
                ],
                "infos": infos,
                "casa": casa,
                "novo_presidente": novo_presidente,
                "contato": contato,
                "comentario_form": ComentarioInternoForm(),
                "ocorrencia_form": OcorrenciaChangeForm(instance=ocorrencia),
            }
        )

        return render(
            request, "ocorrencias/convenio/painel_convenio_detail.html", context
        )

    base_query = Ocorrencia.objects.filter(
        status__in=[Ocorrencia.STATUS_ABERTO, Ocorrencia.STATUS_REABERTO],
        categoria__tipo="C",
    )
    ocorrencias = base_query.filter(infos__has_any_keys=Ocorrencia.INFO_KEYS)
    ocorrencias = ocorrencias.union(
        base_query.exclude(infos__has_any_keys=Ocorrencia.INFO_KEYS)
    )
    context["ocorrencias"] = ocorrencias
    return render(request, "ocorrencias/convenio/painel_convenio.html", context)
