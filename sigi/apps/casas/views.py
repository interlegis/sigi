import csv
from django.db.models import Count, Q, Prefetch, F
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _, ngettext
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)
from django_weasyprint.views import WeasyTemplateResponse
from rest_framework import generics, filters
from sigi.apps.casas.forms import FuncionarioForm, CnpjErradoForm
from sigi.apps.casas.models import Funcionario, Orgao, TipoOrgao
from sigi.apps.casas.serializers import OrgaoAtendidoSerializer
from sigi.apps.home.mixins import ContatoInterlegisViewMixin
from sigi.apps.servidores.models import Servidor
from sigi.apps.contatos.models import (
    UnidadeFederativa,
    Mesorregiao,
    Microrregiao,
)
from sigi.apps.ocorrencias.models import Ocorrencia
from sigi.apps.servicos.models import Servico, TipoServico
from sigi.apps.eventos.models import Evento, TipoEvento
from sigi.apps.convenios.models import Convenio
from sigi.apps.utils import valida_cnpj
from sigi.apps.utils.views import ReportListView


def resumo_carteira(casas):
    regioes = {r[0]: 0 for r in UnidadeFederativa.REGIAO_CHOICES}
    regioes["total"] = 0
    total = regioes.copy()
    sem_produto = regioes.copy()
    tipos_servico = TipoServico.objects.all()
    dados = {ts.id: regioes.copy() for ts in tipos_servico}

    for r in (
        casas.values("municipio__uf__regiao")
        .annotate(quantidade=Count("id"))
        .order_by()
    ):
        regiao = r["municipio__uf__regiao"]
        quantidade = r["quantidade"]
        total[regiao] = quantidade
        total["total"] += quantidade

    for r in (
        casas.filter(servico__data_desativacao=None)
        .order_by()
        # .distinct("id")
        .values("municipio__uf__regiao", "servico__tipo_servico__id")
        .annotate(quantidade=Count("id"))
    ):
        regiao = r["municipio__uf__regiao"]
        servico = r["servico__tipo_servico__id"]
        quantidade = r["quantidade"]
        if servico is None:
            sem_produto[regiao] = quantidade
            sem_produto["total"] += quantidade
        else:
            dados[servico][regiao] = quantidade
            dados[servico]["total"] += quantidade

    dados_ocorrencia = {
        "registradas": regioes.copy(),
        "pendentes": regioes.copy(),
        "sem": regioes.copy(),
        "media": regioes.copy(),
    }

    for r in (
        casas.values("ocorrencia__status", "municipio__uf__regiao")
        .annotate(quantidade=Count("id"))
        .order_by()
    ):
        status = r["ocorrencia__status"]
        regiao = r["municipio__uf__regiao"]
        quantidade = r["quantidade"]
        if status is None:
            dados_ocorrencia["sem"][regiao] += quantidade
            dados_ocorrencia["sem"]["total"] += quantidade
        else:
            dados_ocorrencia["registradas"][regiao] += quantidade
            dados_ocorrencia["registradas"]["total"] += quantidade
            if status in [
                Ocorrencia.STATUS_ABERTO,
                Ocorrencia.STATUS_REABERTO,
            ]:
                dados_ocorrencia["pendentes"][regiao] += quantidade
                dados_ocorrencia["pendentes"]["total"] += quantidade

    for r in regioes:
        if (total[r] - dados_ocorrencia["sem"][r]) == 0:
            dados_ocorrencia["media"][r] = 0
        else:
            dados_ocorrencia["media"][r] = (
                1.0
                * dados_ocorrencia["registradas"][r]
                / (total[r] - dados_ocorrencia["sem"][r])
            )

    resumo = [
        [_("Item"), _("Total nacional")]
        + [r[1] for r in UnidadeFederativa.REGIAO_CHOICES]
    ]
    resumo.append(
        [_("Casas em sua carteira"), total["total"]]
        + [total[r[0]] for r in UnidadeFederativa.REGIAO_CHOICES]
    )
    resumo.append({"subtitle": _("Uso dos produtos Interlegis")})
    resumo.append(
        [_("Casas sem nenhum produto"), sem_produto["total"]]
        + [sem_produto[r[0]] for r in UnidadeFederativa.REGIAO_CHOICES]
    )
    resumo.extend(
        [
            [_(f"Casas usando {ts.nome}"), dados[ts.id]["total"]]
            + [dados[ts.id][r[0]] for r in UnidadeFederativa.REGIAO_CHOICES]
            for ts in tipos_servico
        ]
    )
    resumo.append({"subtitle": _("Registros no sistema de ocorrências")})
    resumo.append(
        [
            _("Casas que nunca registraram ocorrências"),
            dados_ocorrencia["sem"]["total"],
        ]
        + [
            dados_ocorrencia["sem"][r[0]]
            for r in UnidadeFederativa.REGIAO_CHOICES
        ]
    )
    resumo.append(
        [
            _("Total de ocorrências registradas"),
            dados_ocorrencia["registradas"]["total"],
        ]
        + [
            dados_ocorrencia["registradas"][r[0]]
            for r in UnidadeFederativa.REGIAO_CHOICES
        ]
    )
    resumo.append(
        [
            _("Total de ocorrências pendentes"),
            dados_ocorrencia["pendentes"]["total"],
        ]
        + [
            dados_ocorrencia["pendentes"][r[0]]
            for r in UnidadeFederativa.REGIAO_CHOICES
        ]
    )
    resumo.append(
        [
            _("Média de ocorrências por casa"),
            round(dados_ocorrencia["media"]["total"], 2),
        ]
        + [
            round(dados_ocorrencia["media"][r[0]], 2)
            for r in UnidadeFederativa.REGIAO_CHOICES
        ]
    )

    return resumo


def casas_carteira(request, casas, context):
    servicos = request.GET.getlist("servico")
    sigla_regiao = request.GET.get("r", None)
    sigla_uf = request.GET.get("uf", None)
    meso_id = request.GET.get("meso", None)
    micro_id = request.GET.get("micro", None)
    servicos = request.GET.getlist("servico")
    tipos_servico = context["servicos"]

    context["qs_regiao"] = ""

    if micro_id is not None:
        context["micro"] = get_object_or_404(Microrregiao, pk=micro_id)
        context["qs_regiao"] = "micro=%s" % micro_id
        context["meso"] = context["micro"].mesorregiao
        context["uf"] = context["meso"].uf
        context["regiao"] = context["uf"].regiao
        casas = casas.filter(municipio__microrregiao=context["micro"])
    elif meso_id is not None:
        context["meso"] = get_object_or_404(Mesorregiao, pk=meso_id)
        context["qs_regiao"] = "meso=%s" % meso_id
        context["uf"] = context["meso"].uf
        context["regiao"] = context["uf"].regiao
        casas = casas.filter(
            municipio__microrregiao__mesorregiao=context["meso"]
        )
    elif sigla_uf is not None:
        context["uf"] = get_object_or_404(UnidadeFederativa, sigla=sigla_uf)
        context["qs_regiao"] = "uf=%s" % sigla_uf
        context["regiao"] = context["uf"].regiao
        casas = casas.filter(municipio__uf=context["uf"])
    elif sigla_regiao is not None:
        context["regiao"] = sigla_regiao
        context["qs_regiao"] = "r=%s" % sigla_regiao
        casas = casas.filter(municipio__uf__regiao=sigla_regiao)

    if "regiao" in context:
        context["ufs"] = UnidadeFederativa.objects.filter(
            regiao=context["regiao"]
        )

    todos_servicos = ["_none_"] + [s.sigla for s in tipos_servico]

    if not servicos or set(servicos) == set(todos_servicos):
        servicos = todos_servicos
        context["qs_servico"] = ""
    else:
        if "_none_" in servicos:
            casas = casas.filter(
                Q(servico=None) | Q(servico__tipo_servico__sigla__in=servicos)
            )
        else:
            casas = casas.filter(servico__tipo_servico__sigla__in=servicos)
        casas = casas.distinct("nome", "municipio__uf")
        context["qs_servico"] = "&".join(["servico=%s" % s for s in servicos])

    context["servicos_check"] = servicos

    casas = casas.select_related(
        "municipio",
        "municipio__uf",
        "municipio__microrregiao",
        "municipio__microrregiao__mesorregiao",
    ).prefetch_related("servico_set")

    return casas, context


@login_required
@staff_member_required
def painel_relacionamento(request):
    page = request.GET.get("page", 1)
    snippet = request.GET.get("snippet", "")
    seletor = request.GET.get("s", None)
    servidor = request.GET.get("servidor", None)
    fmt = request.GET.get("f", "html")

    if servidor is None:
        gerente = request.user.servidor
    elif servidor == "_all":
        gerente = None
    else:
        gerente = get_object_or_404(Servidor, pk=servidor)

    if gerente is not None:
        casas = gerente.casas_que_gerencia.all()

    if gerente is None or not casas.exists():
        casas = Orgao.objects.exclude(gerentes_interlegis=None)
        gerente = None

    tipos_servico = TipoServico.objects.all()
    regioes = UnidadeFederativa.REGIAO_CHOICES

    context = {
        "seletor": seletor,
        "snippet": snippet,
        "regioes": regioes,
        "servicos": tipos_servico,
        "gerentes": Servidor.objects.exclude(casas_que_gerencia=None),
        "gerente": gerente,
        "qs_servidor": ("servidor=%s" % gerente.pk) if gerente else "",
    }

    if snippet != "lista":
        context["resumo"] = resumo_carteira(casas)

    if snippet != "resumo":
        casas, context = casas_carteira(request, casas, context)
        paginator = Paginator(casas, 30)
        try:
            pagina = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pagina = paginator.page(paginator.num_pages)
        context["page_obj"] = pagina

    if snippet == "lista":
        if fmt == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=casas.csv"
            writer = csv.writer(response)
            writer.writerow(
                [
                    _("Casa legislativa"),
                    _("Região"),
                    _("Estado"),
                    _("Mesorregião"),
                    _("Microrregião"),
                    _("Gerentes Interlegis"),
                    _("Serviços"),
                ]
            )
            for c in casas:
                writer.writerow(
                    [
                        c.nome,
                        c.municipio.uf.get_regiao_display(),
                        c.municipio.uf.sigla,
                        c.municipio.microrregiao.mesorregiao.nome,
                        c.municipio.microrregiao.nome,
                        c.lista_gerentes(fmt="lista"),
                        (
                            ", ".join(
                                [
                                    s.tipo_servico.nome
                                    for s in c.servico_set.filter(
                                        data_desativacao__isnull=True
                                    )
                                ]
                            )
                        ),
                    ]
                )
            return response
        return render(
            request, "casas/lista_casas_carteira_snippet.html", context
        )
    if snippet == "resumo":
        return render(request, "casas/resumo_carteira_snippet.html", context)

    return render(request, "casas/painel.html", context)


class CnpjDuplicadoReport(
    LoginRequiredMixin, UserPassesTestMixin, ReportListView
):
    title = _("Órgãos com CNPJ duplicado")
    empty_message = _("Nenhum órgão com CNPJ duplicado!")
    queryset = Orgao.objects.filter(
        cnpj__in=(
            Orgao.objects.exclude(cnpj="")
            .order_by("cnpj")
            .values("cnpj")
            .annotate(tot=Count("cnpj"))
            .filter(tot__gt=1)
            .values("cnpj")
        )
    ).prefetch_related("tipo", "municipio", "municipio__uf")
    ordering = ["cnpj", "nome", "municipio__nome", "municipio__uf"]
    list_fields = [
        "id",
        "cnpj",
        "tipo__nome",
        "sigla",
        "nome",
        "municipio__nome",
        "municipio__uf__sigla",
    ]
    list_labels = [
        "ID",
        "CNPJ",
        "Tipo de órgão",
        "Sigla",
        "Nome",
        "Cidade",
        "UF",
    ]
    link_fields = ["id"]
    change_field = "cnpj"

    def test_func(self):
        return self.request.user.is_staff

    def get_title(self):
        count = self.get_queryset().count()
        return ngettext(
            "Um órgão com CNPJ duplicado",
            f"{count} órgãos com CNPJ duplicado",
            count,
        )


class CnpjErradoReport(
    LoginRequiredMixin, UserPassesTestMixin, ReportListView
):
    title = _("Órgãos com CNPJ digitado errado")
    empty_message = _("Nenhum órgão com CNPJ digitado errado")
    queryset = (
        Orgao.objects.exclude(cnpj="")
        .order_by("tipo", "cnpj", "nome")
        .annotate(
            tipo_nome=F("tipo__nome"),
            municipio_nome=F("municipio__nome"),
            uf_sigla=F("municipio__uf__sigla"),
        )
    )
    filter_form = CnpjErradoForm
    list_fields = ["id", "cnpj", "sigla", "nome", "municipio_nome", "uf_sigla"]
    list_labels = ["ID", "CNPJ", "Sigla", "Nome", "Cidade", "UF"]
    link_fields = ["id"]
    break_field = "tipo_nome"

    def test_func(self):
        return self.request.user.is_staff

    def get_title(self):
        count = len(self.get_queryset())
        return ngettext(
            "Um órgão com CNPJ digitado errado",
            f"{count} órgãos com CNPJ digitado errado",
            count,
        )

    def filter_queryset(self, queryset):
        form = self.get_filter_form_instance()
        if form.is_valid():
            has_convenio = form.cleaned_data["has_convenio"]
        else:
            has_convenio = False
        if has_convenio:
            queryset = queryset.exclude(convenio=None)
        orgaos = []
        for orgao in queryset:
            if not valida_cnpj(orgao.cnpj):
                orgaos.append(orgao)
        return orgaos

    def get_dataset(self):
        return (
            [
                {f: getattr(o, f) for f in self.list_fields}
                for o in self.get_queryset()
            ],
            self.list_fields,
        )

    def _get_options(self):
        return Orgao._meta


class GerentesListView(PermissionRequiredMixin, ListView):
    template_name = "admin/casas/gerentes_list.html"
    _tipos = None

    def get_tipos(self):
        if self._tipos is None:
            self._tipos = (
                Orgao.objects.exclude(gerentes_interlegis=None)
                .order_by("tipo_id")
                .distinct("tipo")
                .values_list("tipo", flat=True)
            )
        return self._tipos

    def has_permission(self):
        return self.request.user.is_staff

    def get_queryset(self):
        regioes_dict = dict(UnidadeFederativa.REGIAO_CHOICES)
        counters = {
            f"c_{t}": Count("id", filter=Q(tipo__id=t))
            for t in self.get_tipos()
        }
        gerentes = list(
            Servidor.objects.exclude(casas_que_gerencia=None)
            .order_by("nome_completo")
            .annotate(tot_casas=Count("casas_que_gerencia"))
        )

        for gerente in gerentes:
            regioes = [
                (
                    regioes_dict[r],
                    t,
                    gerente.casas_que_gerencia.filter(municipio__uf__regiao=r)
                    .order_by("municipio__uf__nome")
                    .values_list("municipio__uf__sigla", "municipio__uf__nome")
                    .annotate(tot_casas=Count("*"))
                    .annotate(**counters),
                )
                for r, t in gerente.casas_que_gerencia.order_by(
                    "municipio__uf__regiao"
                )
                .values_list("municipio__uf__regiao")
                .annotate(tot_casas=Count("*"))
            ]
            setattr(gerente, "regioes", regioes)
        return gerentes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos_orgao"] = TipoOrgao.objects.filter(
            id__in=self.get_tipos()
        ).order_by("id")
        return context


################################################################################
# Views para site público - acesso dos contatos Interlegis                     #
################################################################################


class CasaUpdateView(
    ContatoInterlegisViewMixin, LoginRequiredMixin, UpdateView
):
    model = Orgao
    fields = [
        "cnpj",
        "data_instalacao",
        "horario_funcionamento",
        "logradouro",
        "bairro",
        "cep",
        "brasao",
        "foto",
        "telefone_geral",
        "email",
        "pagina_web",
    ]
    template_name = "public/casas/orgao_update.html"
    success_url = reverse_lazy("home_index")

    def get_object(self, *args, **kwargs):
        return self.get_casa()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class FuncionarioListView(
    ContatoInterlegisViewMixin, LoginRequiredMixin, ListView
):
    model = Funcionario
    paginate_by = 100
    template_name = "public/casas/funcionario_list.html"

    def get_queryset(self):
        casa = self.get_casa()
        if casa:
            return casa.funcionario_set.exclude(desativado=True)
        else:
            return Funcionario.objects.none()


class FuncionarioCreateView(
    ContatoInterlegisViewMixin, LoginRequiredMixin, CreateView
):
    model = Funcionario
    form_class = FuncionarioForm
    template_name = "public/casas/funcionario_update.html"
    success_url = reverse_lazy("casas:funcionario_listview")

    def get_queryset(self):
        return self.get_casa().funcionario_set.all()

    def form_valid(self, form):
        casa = self.get_casa()
        self.object = form.save(commit=False)
        self.object.casa_legislativa = casa
        self.object.save()
        return super().form_valid(form)


class FuncionarioUpdateView(
    ContatoInterlegisViewMixin, LoginRequiredMixin, UpdateView
):
    model = Funcionario
    form_class = FuncionarioForm
    template_name = "public/casas/funcionario_update.html"
    success_url = reverse_lazy("casas:funcionario_listview")

    def get_object(self, queryset=None):
        casa = self.get_casa()
        return super().get_object(casa.funcionario_set.all())


class FuncionarioDeleteView(
    ContatoInterlegisViewMixin, LoginRequiredMixin, DeleteView
):
    model = Funcionario
    template_name = "public/casas/funcionario_delete.html"
    success_url = reverse_lazy("casas:funcionario_listview")

    def get_object(self, queryset=None):
        casa = self.get_casa()
        return super().get_object(casa.funcionario_set.all())

    def get_context_data(self, **kwargs):
        func = self.get_object()
        casa = self.get_casa()
        User = get_user_model()
        if (
            func.setor == "contato_interlegis"
            and func.nome
            and func.cpf
            and func.identidade
            and User.objects.filter(username=func.email).exists()
        ):
            # Este funcionário pode fazer login #
            excludes = (
                Q(desativado=True)
                | Q(id=func.id)
                | Q(nome="")
                | Q(cpf="")
                | Q(identidade="")
            )
            emails = [f.email for f in casa.funcionario_set.exclude(excludes)]
            unico_login = not User.objects.filter(username__in=emails).exists()
        else:
            unico_login = False
        context = super().get_context_data(**kwargs)
        context["unico_login"] = unico_login
        return context

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.desativado = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ApiOrgaoAtendidoList(generics.ListAPIView):
    """
    Lista os órgãos legislativos atendidos pelo Interlegis.
    """

    serializer_class = OrgaoAtendidoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["search_text"]

    def get_queryset(self):
        sq_servicos = Servico.objects.filter(data_desativacao=None)
        sq_eventos = (
            Evento.objects.exclude(data_inicio=None)
            .exclude(data_termino=None)
            .exclude(tipo_evento__categoria=TipoEvento.CATEGORIA_VISITA)
            .filter(status=Evento.STATUS_REALIZADO)
        )
        queryset = (
            Orgao.objects.filter(tipo__legislativo=True)
            .filter(
                Q(
                    id__in=sq_eventos.order_by()
                    .distinct("casa_anfitria")
                    .values("casa_anfitria_id")
                )
                | Q(
                    id__in=sq_servicos.order_by()
                    .distinct("casa_legislativa")
                    .values("casa_legislativa_id")
                )
            )
            .select_related("municipio", "municipio__uf", "tipo")
            .prefetch_related(
                Prefetch("servico_set", queryset=sq_servicos),
                Prefetch("evento_set", queryset=sq_eventos),
                Prefetch(
                    "convenio_set",
                    queryset=Convenio.objects.select_related("projeto"),
                ),
            )
        ).order_by("municipio__uf__nome", "tipo__nome", "nome")
        if "pk" in self.kwargs:
            queryset = queryset.filter(id=self.kwargs["pk"])
        elif "uf" in self.kwargs:
            queryset = queryset.filter(
                municipio__uf__sigla=self.kwargs["uf"].upper()
            )
        return queryset
