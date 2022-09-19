import calendar
import csv
import datetime
from itertools import cycle
from random import randint, seed
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.sites import site
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render, get_object_or_404, resolve_url
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import (
    TemplateView,
    UpdateView,
    ListView,
    DeleteView,
    CreateView,
)
from django_weasyprint.views import WeasyTemplateResponse
from sigi.apps.casas.models import Funcionario, TipoOrgao, Orgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.convenios.models import Convenio, Projeto
from sigi.apps.eventos.models import TipoEvento, Evento
from sigi.apps.home.models import Cards, Dashboard
from sigi.apps.ocorrencias.models import Ocorrencia
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.servicos.models import TipoServico, Servico
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils import to_ascii


getcolor = (
    lambda s=None: f"#{randint(32,255):02x}{randint(32,255):02x}"
    f"{randint(32,255):02x}"
    if s is None
    else f"{seed(s) or ''}#{randint(32,255):02x}{randint(32,255):02x}"
    f"{randint(32,255):02x}"
)

gethighlight = (
    lambda s=None: f"#{randint(32,255):02x}{randint(32,255):02x}"
    f"{randint(32,255):02x}c0"
    if s is None
    else f"{seed(s) or ''}#{randint(32,255):02x}{randint(32,255):02x}"
    f"{randint(32,255):02x}c0"
)


################################################################################
# Views para controle de acesso
################################################################################


class LoginView(auth_views.LoginView):
    template_name = "registration/login.html"

    def get_default_redirect_url(self):
        if self.request.user.is_staff:
            login_redirect_url = reverse("admin:index")
        else:
            login_redirect_url = settings.LOGIN_REDIRECT_URL
        return resolve_url(self.next_page or login_redirect_url)


class LogoutView(auth_views.LogoutView):
    template_name = "registration/logout.html"


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "material/admin/password_change.html"


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    pass


class PasswordResetView(auth_views.PasswordResetView):
    pass


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    pass


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    pass


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    pass


################################################################################
# Views para site público - acesso dos contatos Interlegis                     #
################################################################################


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home/public_site/index.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        casa_id = self.request.GET.get(
            "id", self.request.session.get("casa_id", None)
        )
        casas = {
            c.id: c for c in Orgao.objects.filter(funcionario__email=user.email)
        }
        if casa_id and int(casa_id) in casas:
            casa = casas[int(casa_id)]
        else:
            if casas:
                casa = list(casas.values())[0]
            else:
                casa = None
        if casa:
            self.request.session["casa_id"] = casa.id
            ocorrencias = casa.ocorrencia_set.filter(
                status__in=[
                    Ocorrencia.STATUS_ABERTO,
                    Ocorrencia.STATUS_REABERTO,
                ]
            )
            servicos = casa.servico_set.filter(data_desativacao=None)
        context = super().get_context_data(**kwargs)
        context["casas"] = casas.values()
        context["casa"] = casa
        context["ocorrencias"] = ocorrencias[:5]
        context["servicos"] = servicos
        return context


################################################################################
# Views e funções do mapa de atuação do Interlegis
################################################################################


def openmap(request):
    reptype = request.GET.get("reptype", None)
    context = {}

    if reptype is None:
        context["tipos_orgao"] = TipoOrgao.objects.filter(legislativo=True)
        context["tipos_servico"] = TipoServico.objects.all()
        context["tipos_convenio"] = Projeto.objects.all()
        context["gerentes"] = Servidor.objects.exclude(casas_que_gerencia=None)
        context["regioes"] = [
            (s, n, UnidadeFederativa.objects.filter(regiao=s))
            for s, n in UnidadeFederativa.REGIAO_CHOICES
        ]
        return render(request, "home/openmap.html", context)
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        tipos_orgao = request.GET.getlist("tipo_orgao", [])
        tipos_servico = request.GET.getlist("tipo_servico", [])
        tipos_convenio = request.GET.getlist("tipo_convenio", [])
        gerentes = request.GET.getlist("gerente", [])
        ufs = request.GET.getlist("uf", [])
        casas = openmapdata(request)

        context["tipos_orgao"] = TipoOrgao.objects.filter(
            legislativo=True, sigla__in=tipos_orgao
        )
        context["tipos_servico"] = TipoServico.objects.filter(
            sigla__in=tipos_servico
        )
        context["tipos_convenio"] = Projeto.objects.filter(
            sigla__in=tipos_convenio
        )
        context["gerentes"] = Servidor.objects.exclude(
            casas_que_gerencia=None
        ).filter(id__in=gerentes)
        context["ufs"] = UnidadeFederativa.objects.filter(sigla__in=ufs)
        context["casas"] = casas

        if reptype == "lista":
            return WeasyTemplateResponse(
                filename="Lista de Casas atendidas.pdf",
                request=request,
                template="home/lista_casas.html",
                context=context,
                content_type="application/pdf",
            )
        else:
            fields = [
                "cnpj",
                "nome",
                "municipio__uf__nome",
                "municipio__uf__regiao",
                "logradouro",
                "bairro",
                "cep",
                "ult_alt_endereco",
                "email",
            ]
            if reptype in ("exporta_servico", "exporta"):
                fields.extend(
                    [
                        "servico__tipo_servico__nome",
                        "servico__url",
                        "servico__data_ativacao",
                        "servico__data_desativacao",
                    ]
                )
            if reptype in ("exporta_convenio", "exporta"):
                fields.extend(
                    [
                        "convenio__num_convenio",
                        "convenio__num_processo_sf",
                        "convenio__projeto__sigla",
                        "convenio__data_adesao",
                        "convenio__data_termino_vigencia",
                        "convenio__data_retorno_assinatura",
                    ]
                )
            if reptype in ("exporta_contato", "exporta"):
                fields.extend(
                    [
                        "funcionario__nome",
                        "funcionario__setor",
                        "funcionario__email",
                        "funcionario__nota",
                        "funcionario__redes_sociais",
                        "funcionario__desativado",
                        "funcionario__ult_alteracao",
                    ]
                )

            dados = casas.distinct().values(*fields)
            response = HttpResponse(content_type="text/csv")
            writer = csv.DictWriter(response, fieldnames=fields)
            writer.writeheader()
            writer.writerows(dados)
            return response


def openmapdata(request):
    tipos_orgao = request.GET.getlist("tipo_orgao", None)
    tipos_servico = request.GET.getlist("tipo_servico", None)
    tipos_convenio = request.GET.getlist("tipo_convenio", None)
    ufs = request.GET.getlist("uf", None)
    gerentes = request.GET.getlist("gerente", None)
    reptype = request.GET.get("reptype", None)

    dados = Orgao.objects.all()

    if tipos_orgao:
        dados = dados.filter(tipo__sigla__in=tipos_orgao)
    else:
        dados = dados.filter(tipo__legislativo=True)

    if tipos_servico:
        if "none" in tipos_servico:
            dados = dados.filter(servico=None)
        else:
            dados = dados.filter(
                servico__tipo_servico__sigla__in=tipos_servico,
                servico__data_desativacao=None,
            )

    if tipos_convenio:
        if "none" in tipos_convenio:
            dados = dados.filter(convenio=None)
        else:
            dados = dados.filter(convenio__projeto__sigla__in=tipos_convenio)

    if ufs:
        dados = dados.filter(municipio__uf__sigla__in=ufs)

    if gerentes:
        if "none" in gerentes:
            dados = dados.filter(gerentes_interlegis=None)
        else:
            dados = dados.filter(gerentes_interlegis__id__in=gerentes)

    if not reptype:
        dados = dados.order_by("nome", "id").distinct("nome", "id")
        dados = dados.values_list(
            "id", "nome", "municipio__latitude", "municipio__longitude"
        )
        return JsonResponse(list(dados), safe=False)
    else:
        dados = (
            dados.order_by(
                "municipio__uf__regiao", "municipio__uf__nome", "nome", "id"
            )
            .distinct(
                "municipio__uf__regiao", "municipio__uf__nome", "nome", "id"
            )
            .prefetch_related(
                "servico_set",
                "convenio_set",
                "municipio__uf",
                "gerentes_interlegis",
            )
        )
        return dados


def openmapdetail(request, orgao_id):
    orgao = get_object_or_404(Orgao, id=orgao_id)
    return render(request, "home/openmapdetail.html", {"orgao": orgao})


def openmapsearch(request):
    q = request.GET.get("q", "")
    if len(q) < 3:
        return JsonResponse({"result": "unsearchable"})

    dados = Orgao.objects.filter(
        tipo__legislativo=True, search_text__icontains=to_ascii(q)
    )[:10]
    dados = dados.values(
        "id",
        "nome",
        "municipio__uf__sigla",
        "municipio__latitude",
        "municipio__longitude",
    )
    dados = [
        {
            "id": d["id"],
            "label": f"{d['nome']} - {d['municipio__uf__sigla']}",
            "lat": d["municipio__latitude"],
            "lng": d["municipio__longitude"],
        }
        for d in dados
    ]
    return JsonResponse(list(dados), safe=False)


################################################################################
# Views de visualização e edição do dashboard
################################################################################


@xframe_options_exempt
def card_snippet(request, card_code):
    card = get_object_or_404(Cards, codigo=card_code)
    if not card.default:
        raise PermissionDenied()
    return render(request, "home/dashboard/card.html", {"card": card})


@login_required
def card_add_tab(request, tab_slug):
    total = 0
    categoria = tab_slug
    for card in Cards.objects.all():
        if slugify(card.categoria) == tab_slug:
            categoria = card.categoria
            __, created = Dashboard.objects.update_or_create(
                defaults={"ordem": card.ordem},
                usuario=request.user,
                card=card,
                categoria=card.categoria,
            )
            if created:
                total += 1
    messages.info(request, _(f"{total} cards adicionados na aba {categoria}"))
    return HttpResponseRedirect(reverse("admin:index"))


@login_required
def card_rename_tab(request):
    dados = request.POST.copy()
    dados.pop("csrfmiddlewaretoken")
    categoria_atual = dados.pop("categoria_atual")[0]
    categoria_nova = dados.pop("categoria_nova")[0]
    if categoria_nova != "" and categoria_nova != categoria_atual:
        Dashboard.objects.filter(
            usuario=request.user, categoria=categoria_atual
        ).update(categoria=categoria_nova)
        messages.success(request, _("Tab renomeada com sucesso"))
    else:
        messages.warning(request, _("Não foi possível renomear a tab"))
    return HttpResponseRedirect(reverse("admin:index"))


@login_required
def card_reorder(request):
    dados = request.GET.copy()
    categoria = dados.pop("categoria")[0]
    for codigo, nova_ordem in dados.items():
        Dashboard.objects.filter(
            usuario=request.user, card__codigo=codigo, categoria=categoria
        ).update(ordem=nova_ordem)
    return JsonResponse({"result": _("Ordem alterada")})


@login_required
def card_remove(request, categoria, codigo):
    count, *__ = Dashboard.objects.filter(
        categoria=categoria, card__codigo=codigo
    ).delete()
    return JsonResponse({"result": _(f"{count} card(s) removido(s)")})


@login_required
def card_add(request):
    categoria = request.POST.get("categoria", None)
    codigos = request.POST.getlist("card_id", None)

    if categoria is None or codigos is None:
        messages.error(request, _("Nenhum card adicionado!"))
    else:
        criados = 0
        for codigo in codigos:
            card = get_object_or_404(Cards, codigo=codigo)
            dash, created = Dashboard.objects.get_or_create(
                {"ordem": card.ordem},
                usuario=request.user,
                card=card,
                categoria=categoria,
            )
            if created:
                criados += 1
        if criados > 0:
            messages.success(
                request, _(f"{criados} card(s) adicionado(s) na aba")
            )
        else:
            messages.info(request, _("Estes cards já estão na aba"))
    return HttpResponseRedirect(reverse("admin:index"))


################################################################################
# Cards do dashboard
################################################################################


# Geral ########################################################################


@never_cache
@login_required
def resumo_convenios(request):
    context = {"tabela_resumo_camara": busca_informacoes_camara()}
    return render(request, "home/dashboard/resumo_convenios.html", context)


# Serviços #####################################################################


@never_cache
@login_required
def resumo_seit(request):
    mes = request.GET.get("mes", None)
    ano = request.GET.get("ano", None)

    try:
        mes = datetime.date(year=int(ano), month=int(mes), day=1)
        tabela_resumo_seit = busca_informacoes_seit(mes)
    except:
        tabela_resumo_seit = busca_informacoes_seit()

    context = {"tabela_resumo_seit": tabela_resumo_seit}
    return render(request, "home/dashboard/resumo_seit.html", context)


@never_cache
@login_required
def chart_seit(request):
    hoje = timezone.localdate()
    mes = request.GET.get("mes", hoje.month)
    ano = request.GET.get("ano", hoje.year)

    mes = datetime.date(year=int(ano), month=int(mes), day=1)
    tabela_resumo_seit = busca_informacoes_seit(mes)

    data = {
        "type": "line",
        "prevlink": reverse("home_chartseit")
        + (
            f"?ano={tabela_resumo_seit['mes_anterior'].year}"
            f"&mes={tabela_resumo_seit['mes_anterior'].month}"
        ),
        "nextlink": reverse("home_chartseit")
        + (
            f"?ano={tabela_resumo_seit['proximo_mes'].year}"
            f"&mes={tabela_resumo_seit['proximo_mes'].month}"
        ),
        "options": {
            "bezierCurve": False,
            "datasetFill": False,
            "pointDot": False,
            "responsive": True,
        },
        "data": {
            "labels": [
                f"{mes: %m/%Y}" for mes in reversed(tabela_resumo_seit["meses"])
            ],
            "datasets": [
                {
                    "label": servico["nome"],
                    "borderColor": servico["cor"],
                    "backgroundColor": servico["cor"],
                    "data": [
                        mes["total"]
                        for mes in reversed(servico["novos_por_mes"])
                    ],
                }
                for servico in tabela_resumo_seit["servicos"]
            ],
        },
    }

    return JsonResponse(data)


@never_cache
@login_required
def chart_uso_servico(request):
    ufs = UnidadeFederativa.objects.all()
    sigla_uf = request.GET.get("uf", "_all")

    if sigla_uf != "_all":
        uf = get_object_or_404(UnidadeFederativa, sigla=sigla_uf)
    else:
        uf = None

    counts = {
        f"{key}_count": Count("servico", Q(servico__resultado_verificacao=key))
        for key, *__ in Servico.RESULTADO_CHOICES
    }

    queryset = TipoServico.objects.exclude(string_pesquisa="").filter(
        servico__data_desativacao=None
    )

    if uf is not None:
        queryset = queryset.filter(servico__casa_legislativa__municipio__uf=uf)

    queryset = queryset.annotate(**counts)

    chart = {
        "data": {
            "datasets": [
                {
                    "type": "bar",
                    "label": label,
                    "data": list(
                        queryset.values_list(f"{key}_count", flat=True)
                    ),
                    "backgroundColor": getcolor(label),
                }
                for key, label in Servico.RESULTADO_CHOICES
            ],
            "labels": list(queryset.values_list("sigla", flat=True)),
        },
        "actionblock": render_to_string(
            "home/dashboard/ufs_snippet.html",
            context={"ufs": ufs, "uf": uf},
            request=request,
        ),
    }

    return JsonResponse(chart)


@never_cache
@login_required
def chart_atualizacao_servicos(request):
    intervalos = [
        ("Na semana", 7),
        ("No mês", 30),
        ("No trimestre", 3 * 30),
        ("No semestre", 6 * 30),
        ("No ano", 365),
        ("Mais de ano", None),
    ]

    counts = {}
    hoje = timezone.localdate()
    ate = hoje

    for label, dias in intervalos:
        if dias is not None:
            de = hoje - datetime.timedelta(days=dias)
            counts[slugify(label)] = Count(
                "servico", Q(servico__data_ultimo_uso__range=(de, ate))
            )
            ate = de - datetime.timedelta(days=1)
        else:
            counts[slugify(label)] = Count(
                "servico", Q(servico__data_ultimo_uso__lte=ate)
            )

    queryset = (
        TipoServico.objects.exclude(string_pesquisa="")
        .filter(servico__data_desativacao=None)
        .annotate(**counts)
    )

    chart = {
        "data": {
            "datasets": [
                {
                    "type": "bar",
                    "label": ts.sigla,
                    "data": [
                        getattr(ts, slugify(label)) for label, *__ in intervalos
                    ],
                    "backgroundColor": getcolor(ts.nome),
                }
                for ts in queryset
            ],
            "labels": [label for label, *__ in intervalos],
        }
    }

    return JsonResponse(chart)


# Gerente ######################################################################


@never_cache
@login_required
def chart_carteira(request):
    gerentes = Servidor.objects.exclude(casas_que_gerencia=None).annotate(
        total_casas=Count("casas_que_gerencia")
    )

    data = {
        "type": "doughnut",
        "data": {
            "labels": [g.get_apelido() for g in gerentes],
            "datasets": [
                {
                    "data": [g.total_casas for g in gerentes],
                    "backgroundColor": [
                        gethighlight(g.get_apelido()) for g in gerentes
                    ],
                }
            ],
        },
    }

    return JsonResponse(data)


@never_cache
@login_required
def chart_performance(request):
    servidor = request.GET.get("servidor", None)
    gerentes = Servidor.objects.exclude(casas_que_gerencia=None)
    gerente = None

    if servidor is None:
        if (
            request.user.servidor
            and request.user.servidor.casas_que_gerencia.exists()
        ):
            gerente = request.user.servidor
        else:
            servidor = "_all"

    if servidor is not None and servidor != "_all":
        gerente = get_object_or_404(Servidor, pk=servidor)

    if gerente is None:
        casas = Orgao.objects.exclude(gerentes_interlegis=None)
    else:
        casas = gerente.casas_que_gerencia

    data = {
        "type": "doughnut",
        "data": {
            "labels": [_("Utilizam serviços"), _("Não utilizam serviços")],
            "datasets": [
                {
                    "label": _("Uso dos serviços"),
                    "data": [
                        casas.exclude(servico=None).count(),
                        casas.filter(servico=None).count(),
                    ],
                    "backgroundColor": ["#91e8e1", "#f7a35c"],
                }
            ],
        },
        "actionblock": render_to_string(
            "home/dashboard/gerentes_snippet.html",
            context={"gerentes": gerentes, "gerente": gerente},
            request=request,
        ),
    }

    return JsonResponse(data)


# Eventos ######################################################################


@never_cache
@login_required
def eventos_status(request):
    queryset = Evento.objects.values("status").annotate(total=Count("id", Q()))
    statuses = dict(Evento.STATUS_CHOICES)

    chart = {
        "type": "doughnut",
        "data": {
            "datasets": [
                {
                    "label": _("Eventos por status"),
                    "data": [e["total"] for e in queryset],
                    "backgroundColor": [
                        getcolor(statuses[e["status"]]) for e in queryset
                    ],
                }
            ],
            "labels": [statuses[e["status"]] for e in queryset],
        },
    }
    return JsonResponse(chart)


@never_cache
@login_required
def eventos_categoria(request):
    queryset = (
        TipoEvento.objects.filter(evento__status="R")
        .values("categoria")
        .annotate(total=Count("evento"))
    )
    categorias = dict(TipoEvento.CATEGORIA_CHOICES)

    chart = {
        "type": "doughnut",
        "data": {
            "datasets": [
                {
                    "label": _("Eventos por categoria"),
                    "data": [e["total"] for e in queryset],
                    "backgroundColor": [
                        getcolor(categorias[e["categoria"]]) for e in queryset
                    ],
                }
            ],
            "labels": [categorias[e["categoria"]] for e in queryset],
        },
    }
    return JsonResponse(chart)


@never_cache
@login_required
def eventos_ano(request):
    mes = request.GET.get("mes", timezone.localdate().month)
    ano = request.GET.get("ano", timezone.localdate().year)

    mes = datetime.date(year=int(ano), month=int(mes), day=1)
    mes_anterior = mes - datetime.timedelta(days=1)
    proximo_mes = mes + datetime.timedelta(
        days=calendar.monthrange(mes.year, mes.month)[1]
    )

    meses = []
    counts = {}
    start = mes

    for i in range(12):
        meses.append(start)
        counts[f"{start:%m/%Y}"] = Count(
            "evento",
            Q(
                evento__data_inicio__year=start.year,
                evento__data_inicio__month=start.month,
            ),
        )
        start = (start - datetime.timedelta(days=1)).replace(day=1)

    queryset = (
        TipoEvento.objects.filter(evento__status="R")
        .values("categoria")
        .annotate(**counts)
    )
    categorias = dict(TipoEvento.CATEGORIA_CHOICES)

    chart = {
        "type": "line",
        "prevlink": reverse("eventos_ano")
        + f"?ano={mes_anterior.year}&mes={mes_anterior.month}",
        "nextlink": reverse("eventos_ano")
        + f"?ano={proximo_mes.year}&mes={proximo_mes.month}",
        "options": {
            "bezierCurve": False,
            "datasetFill": False,
            "pointDot": False,
            "responsive": True,
        },
        "data": {
            "labels": [f"{mes: %m/%Y}" for mes in reversed(meses)],
            "datasets": [
                {
                    "label": categorias[rec["categoria"]],
                    "borderColor": getcolor(categorias[rec["categoria"]]),
                    "backgroundColor": getcolor(categorias[rec["categoria"]]),
                    "data": [rec[f"{mes:%m/%Y}"] for mes in reversed(meses)],
                }
                for rec in queryset
            ],
        },
    }

    return JsonResponse(chart)


################################################################################
# Views de apoio e relatórios
################################################################################


@never_cache
@login_required
def report_sem_convenio(request):
    modo = request.GET.get("modo", None)
    fmt = request.GET.get("f", "pdf")

    sc = sem_convenio()

    if modo == "H":
        casas = sc["hospedagem"]
        titulo = _(
            "Casas sem convenio que utilizam algum serviço de " "hospedagem"
        )
    elif modo == "R":
        casas = sc["registro"]
        titulo = _(
            "Casas sem convenio que utilizam somente serviço de " "registro"
        )
    else:
        casas = sc["total"]
        titulo = _(
            "Casas sem convenio que utilizam algum serviço de registro "
            "e/ou hospedagem"
        )

    if fmt == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={ titulo }.csv"
        writer = csv.writer(response)
        writer.writerow([titulo])
        writer.writerow([""])
        writer.writerow(["casa", "uf", "gerentes", "serviços"])
        for casa in casas:
            writer.writerow(
                [
                    casa.nome,
                    casa.municipio.uf.sigla,
                    casa.lista_gerentes(fmt="lista"),
                    (
                        ", ".join(
                            casa.servico_set.filter(
                                data_desativacao__isnull=True
                            ).values_list("tipo_servico__nome", flat=True)
                        )
                    ),
                ]
            )
        return response
    elif fmt == "json":
        data = {
            "titulo": titulo,
            "casas": [
                {
                    "nome": casa.nome,
                    "uf": casa.municipio.uf.sigla,
                    "gerentes": list(
                        casa.gerentes_interlegis.all().values_list(
                            "nome_completo", flat=True
                        )
                    ),
                    "servicos": list(
                        casa.servico_set.filter(
                            data_desativacao__isnull=True
                        ).values_list("tipo_servico__nome", flat=True)
                    ),
                }
                for casa in casas
            ],
        }
        return JsonResponse(data, safe=False)
    else:
        context = {"casas": casas, "title": titulo}
        return WeasyTemplateResponse(
            filename=f"{ titulo }.pdf",
            request=request,
            template="home/sem_convenio.html",
            context=context,
            content_type="application/pdf",
        )


def busca_informacoes_camara():
    camaras = Orgao.objects.filter(tipo__sigla="CM")
    convenios = Convenio.objects.filter(casa_legislativa__tipo__sigla="CM")
    projetos = Projeto.objects.all()

    convenios_assinados = convenios.exclude(data_retorno_assinatura=None)
    convenios_em_andamento = convenios.filter(data_retorno_assinatura=None)

    convenios_sem_adesao = convenios.filter(data_adesao=None)
    convenios_com_adesao = convenios.exclude(data_adesao=None)

    convenios_com_aceite = convenios.exclude(data_termo_aceite=None)

    camaras_sem_processo = camaras.filter(convenio=None)

    # Criacao das listas para o resumo de camaras por projeto

    cabecalho_topo = [
        "",
    ]  # Cabecalho superior da tabela

    lista_total = []
    lista_nao_aderidas = []
    lista_aderidas = []
    lista_convenios_assinados = []
    lista_convenios_em_andamento = []
    lista_camaras_equipadas = []
    for projeto in projetos:
        conv_sem_adesao_proj = convenios_sem_adesao.filter(projeto=projeto)
        conv_com_adesao_proj = convenios_com_adesao.filter(projeto=projeto)
        conv_assinados_proj = convenios_assinados.filter(projeto=projeto)
        conv_em_andamento_proj = convenios_em_andamento.filter(projeto=projeto)
        conv_equipadas_proj = convenios_com_aceite.filter(projeto=projeto)

        cabecalho_topo.append(projeto.sigla)
        lista_total.append(camaras.filter(convenio__projeto=projeto).count())
        lista_nao_aderidas.append(
            camaras.filter(convenio__in=conv_sem_adesao_proj).count()
        )
        lista_aderidas.append(
            camaras.filter(convenio__in=conv_com_adesao_proj).count()
        )
        lista_convenios_assinados.append(
            camaras.filter(convenio__in=conv_assinados_proj).count()
        )
        lista_convenios_em_andamento.append(
            camaras.filter(convenio__in=conv_em_andamento_proj).count()
        )
        lista_camaras_equipadas.append(
            camaras.filter(convenio__in=conv_equipadas_proj).count()
        )

    # Cabecalho da esquerda na tabela
    cabecalho_esquerda = (
        _("Câmaras municipais"),
        _("Câmaras municipais não aderidas"),
        _("Câmaras municipais aderidas"),
        _("Câmaras municipais com convênios assinados"),
        _("Câmaras municipais convênios em andamento"),
        _("Câmaras municipais equipadas"),
    )

    linhas = (
        lista_total,
        lista_nao_aderidas,
        lista_aderidas,
        lista_convenios_assinados,
        lista_convenios_em_andamento,
        lista_camaras_equipadas,
    )

    # Unindo as duas listas para que o cabecalho da esquerda fique junto com sua
    # respectiva linha
    lista_zip = zip(cabecalho_esquerda, linhas)

    # Retornando listas em forma de dicionario
    return {
        "cabecalho_topo": cabecalho_topo,
        "lista_zip": lista_zip,
        "total_camaras": camaras.count(),
        "camaras_sem_processo": camaras_sem_processo.count(),
        "sem_convenio": sem_convenio(),
    }


def sem_convenio():
    total = (
        Orgao.objects.exclude(servico=None)
        .filter(servico__data_desativacao=None, convenio=None)
        .order_by("municipio__uf__sigla", "nome")
        .distinct("municipio__uf__sigla", "nome")
    )
    hospedagem = (
        Orgao.objects.exclude(servico=None)
        .filter(
            servico__data_desativacao=None,
            servico__tipo_servico__modo="H",
            convenio=None,
        )
        .order_by("municipio__uf__sigla", "nome")
        .distinct("municipio__uf__sigla", "nome")
    )
    reg_keys = set(total.values_list("pk", flat=True)).difference(
        set(hospedagem.values_list("pk", flat=True))
    )
    registro = Orgao.objects.filter(pk__in=reg_keys).order_by(
        "municipio__uf__sigla", "nome"
    )
    return {
        "total": total,
        "hospedagem": hospedagem,
        "registro": registro,
    }


def busca_informacoes_seit(mes_atual=None):
    if mes_atual is None:
        mes_atual = datetime.date.today().replace(day=1)
    mes_anterior = mes_atual - datetime.timedelta(days=1)
    proximo_mes = mes_atual + datetime.timedelta(
        days=calendar.monthrange(mes_atual.year, mes_atual.month)[1]
    )

    meses = []
    mes = mes_atual
    for i in range(1, 13):
        meses.append(mes)
        mes = (mes - datetime.timedelta(days=1)).replace(day=1)

    result = {
        "mes_atual": mes_atual,
        "mes_anterior": mes_anterior,
        "proximo_mes": proximo_mes,
        "meses": meses,
        "titulos": [
            "",
            "Total de casas atendidas",
            "Novas casas em %s/%s" % (mes_anterior.month, mes_anterior.year),
            "Novas casas em %s/%s" % (mes_atual.month, mes_atual.year),
        ],
        "servicos": [],
    }

    for tipo_servico in TipoServico.objects.all():
        por_mes = []
        for mes in meses:
            por_mes.append(
                {
                    "mes": f"{mes:%m/%Y}",
                    "total": tipo_servico.servico_set.filter(
                        data_ativacao__year=mes.year,
                        data_ativacao__month=mes.month,
                    ).count(),
                }
            )

        result["servicos"].append(
            {
                "nome": tipo_servico.nome,
                "total": tipo_servico.servico_set.filter(
                    Q(data_ativacao__lt=proximo_mes)
                    & (
                        Q(data_desativacao=None)
                        | Q(data_desativacao__gt=proximo_mes)
                    )
                ).count(),
                "novos_mes_anterior": tipo_servico.servico_set.filter(
                    data_ativacao__year=mes_anterior.year,
                    data_ativacao__month=mes_anterior.month,
                ).count(),
                "novos_mes_atual": tipo_servico.servico_set.filter(
                    data_ativacao__year=mes_atual.year,
                    data_ativacao__month=mes_atual.month,
                ).count(),
                "novos_por_mes": por_mes,
                "cor": getcolor(tipo_servico.nome),
            }
        )

    return result


def color_palete():
    colors = cycle(
        [
            "#7cb5ec",
            "#434348",
            "#90ed7d",
            "#f7a35c",
            "#8085e9",
            "#f15c80",
            "#e4d354",
            "#8085e8",
            "#8d4653",
            "#91e8e1",
        ]
    )

    highlights = cycle(
        [
            "#B0D3F4",
            "#8E8E91",
            "#BCF4B1",
            "#FAC89D",
            "#B3B6F2",
            "#F79DB3",
            "#EFE598",
            "#B3B6F1",
            "#BB9098",
            "#BDF1ED",
        ]
    )

    return (colors, highlights)


# @never_cache
# @login_required
# def index(request):
#     context = {'gerentes': Servidor.objects.exclude(casas_que_gerencia=None)}
#     return render(request, 'index.html', context)

# def grafico_convenio_projeto(convenios):
#     colors, highlights = color_palete()
#     projetos = Projeto.objects.all()
#     lista_projetos = [{'label': projeto.sigla,
#                        'value': convenios.filter(projeto=projeto).count(),
#                        'color': colors.next(),
#                        'highlight': highlights.next()}
#                       for projeto in projetos]
#     # remove projetos sem convenio
#     lista_projetos = [x for x in lista_projetos if x['value'] > 0]

#     # print lista_projetos
#     # total_convenios = "Total: " + str(convenios.count())
#     # lista_projetos.insert(0, total_convenios)
#     return lista_projetos

# @never_cache
# @login_required
# def chart_convenios(request):
#     q = request.GET.get('q', 'all')
#     convenios = Convenio.objects.all()
#     if q == 'assinados':
#         convenios = convenios.exclude(data_retorno_assinatura=None)
#     data = {
#         'type': 'pie',
#         'options': {'responsive': False, 'maintainAspectRatio': False},
#         'data': grafico_convenio_projeto(convenios),
#     }
#     return JsonResponse(data)

# def busca_informacoes_diagnostico():
#     return [
#         {'title': _('Diagnósticos digitados'), 'count': Diagnostico.objects.count()},
#         {'title': _('Diagnósticos publicados'), 'count': Diagnostico.objects.filter(publicado=True).count()},
#     ]
