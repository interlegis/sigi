from sys import prefix
from django.conf import settings
import django_filters
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.message import EmailMessage
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.template.loader import render_to_string
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.html import escape, quote
from django.utils.translation import ngettext, gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django_weasyprint.utils import django_url_fetcher
from weasyprint import HTML
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.eventos.models import Evento
from sigi.apps.home.mixins import ContatoInterlegisViewMixin
from sigi.apps.ocorrencias.models import (
    Categoria,
    Comentario,
    Ocorrencia,
    Anexo,
    TipoContato,
)
from sigi.apps.ocorrencias.forms import (
    AnexoForm,
    AutorizaOficinaForm,
    ComentarioForm,
    ComentarioInternoForm,
    ContatoForm,
    DocumentoForm,
    OcorrenciaChangeForm,
    OcorrenciaForm,
    CasaForm,
    PresidenteForm,
    SolicitaTreinamentoForm,
)
from sigi.apps.parlamentares.models import Parlamentar, Senador
from sigi.apps.servidores.models import Servidor, Servico
from sigi.apps.utils import to_ascii


class PainelOcorrenciaFilter(django_filters.FilterSet):
    status = django_filters.MultipleChoiceFilter(
        label=_("Status"),
        field_name="status",
        choices=Ocorrencia.STATUS_CHOICES,
    )
    nome_casa = django_filters.CharFilter(
        label=_("Nome da casa contém"),
        field_name="casa_legislativa__search_text",
        lookup_expr=_("icontains"),
    )
    gerente = django_filters.ModelChoiceFilter(
        label=_("Casas gerenciadas por"),
        field_name="casa_legislativa__gerentes_interlegis",
        queryset=Servidor.objects.exclude(user__is_active=False).exclude(
            casas_que_gerencia=None
        ),
    )
    servidor = django_filters.ModelChoiceFilter(
        label=_("Ocorrências registradas ou comentadas por"),
        method="servidor_filter",
        queryset=Servidor.objects.exclude(user__is_active=False).exclude(
            ocorrencia=None, comentario=None
        ),
    )
    tipo_categoria = django_filters.ChoiceFilter(
        label=_("Tipo de ocorrência"),
        field_name="categoria__tipo",
        choices=Categoria.TIPO_CHOICES,
    )
    categoria = django_filters.ModelChoiceFilter(
        label=_("Categoria"),
        field_name="categoria",
        queryset=Categoria.objects.all(),
    )

    class Meta:
        model = Ocorrencia
        fields = [
            "nome_casa",
            "gerente",
            "servidor",
            "tipo_categoria",
            "categoria",
        ]

    def servidor_filter(self, queryset, name, value):
        return queryset.filter(
            Q(servidor_registro=value) | Q(comentarios__usuario=value)
        )

    def preserve_filter(self):
        if not self.data:
            return ""
        data = self.data.copy()
        filterlist = self.get_filters().keys()
        data_keys = list(data.keys())
        for key in data_keys:
            if key not in filterlist:
                data.pop(key)
        return data.urlencode()


def bound_copy(instance, bound_data, removes=None):
    data = bound_data.copy()
    if removes:
        for remove_key in removes:
            data.pop(remove_key)
    for key, value in data.items():
        setattr(instance, key, value)


class PainelOcorrenciaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Ocorrencia
    context_object_name = "ocorrencias"
    filter_class = PainelOcorrenciaFilter
    paginate_by = 100
    template_name = "ocorrencias/painel.html"
    panel_title = _("Painel de ocorrências")

    def test_func(self):
        return self.request.user.is_staff

    def get_filter(self, request, queryset=None):
        klass = self.filter_class
        return klass(request.GET, queryset=queryset)

    def get_subtitles(self, filter):
        subts = []
        if filter.data:
            if filter.data.get("nome_casa"):
                subts.append(
                    _(f"Casas com \"{filter.data.get('nome_casa')}\" no nome")
                )
            if filter.data.get("gerente"):
                gerente = Servidor.objects.get(id=filter.data.get("gerente"))
                subts.append(
                    _(f"Casas gerenciadas por {gerente.get_apelido()}")
                )
            if filter.data.get("servidor"):
                servidor = Servidor.objects.get(id=filter.data.get("servidor"))
                subts.append(
                    _(
                        f"Registradas ou comentadas por {servidor.get_apelido()}"
                    )
                )
            if filter.data.get("tipo_categoria"):
                tipo = dict(Categoria.TIPO_CHOICES)[
                    filter.data.get("tipo_categoria")
                ]
                subts.append(_(f"Do tipo {tipo}"))
            if filter.data.get("categoria"):
                categoria = Categoria.objects.get(
                    id=filter.data.get("categoria")
                )
                subts.append(_(f"Da categoria {categoria.nome}"))
            if filter.data.getlist("status"):
                status_names = dict(Ocorrencia.STATUS_CHOICES)
                subts.append(
                    _("Status: ")
                    + " - ".join(
                        [
                            status_names[int(s)]
                            for s in filter.data.getlist("status")
                        ]
                    )
                )
        return subts

    def get_queryset(self):
        queryset = super().get_queryset()
        filter = self.get_filter(self.request, queryset)
        return filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = self.get_filter(self.request)
        context["panel_title"] = self.panel_title
        context["panel_subtitles"] = self.get_subtitles(filter)
        context["filter"] = filter
        context["has_add_permission"] = self.request.user.has_perm(
            "ocorrencias.add_ocorrencia"
        )
        context["has_change_permission"] = self.request.user.has_perm(
            "ocorrencias.change_ocorrencia"
        )
        return context


class BaseOcorrenciaChangeView(
    LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    template_name = "ocorrencias/ocorrencia_detail.html"
    model = Ocorrencia
    form_class = OcorrenciaChangeForm
    list_filter = ""
    # Adicionar todas as classes de form nesta tupla

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        if not self.success_url_name:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Provide a url name."
            )

        url = reverse(
            self.success_url_name, kwargs={"pk": self.get_object().pk}
        )
        if self.list_filter:
            return f"{url}?list_filter={quote(self.list_filter)}"

    def get_form_classes(self):
        form_classes = {
            "ocorrencia": OcorrenciaChangeForm,
            "comentario": ComentarioInternoForm,
        }
        if hasattr(self, "form_classes"):
            form_classes.update(self.form_classes)
        return form_classes

    def get_form(self, name=None):
        form_classes = self.get_form_classes()
        if name is None:
            name = list(form_classes.keys())[
                list(form_classes.values()).index(self.get_form_class())
            ]
        form_class = form_classes[name]
        kwargs = self.get_form_kwargs()
        kwargs["prefix"] = name
        if hasattr(self, f"get_{name}_form_kwargs"):
            f = getattr(self, f"get_{name}_form_kwargs")
            kwargs.update(f())
        return form_class(**kwargs)

    def get_comentario_form_kwargs(self):
        ocorrencia = self.get_object()
        if self.request.user.servidor:
            usuario = self.request.user.servidor
        else:
            usuario = Servidor.objects.get(sigi=True)
        return {"instance": Comentario(ocorrencia=ocorrencia, usuario=usuario)}

    def get(self, request, *args, **kwargs):
        self.list_filter = request.GET.get("list_filter", "")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.list_filter = request.GET.get("list_filter", "")
        self.object = self.get_object()
        for name in self.get_form_classes():
            if f"save_{name}_form" in request.POST:
                form = self.get_form(name)
                if form.is_valid():
                    form_valid_method = getattr(
                        self, f"form_{name}_valid", self.form_valid
                    )
                    return form_valid_method(form)
                else:
                    form_invalid_method = getattr(
                        self, f"form_{name}_invalid", self.form_invalid
                    )
                    return form_invalid_method(form)
        messages.warning(request, _("Nenhuma alteração salva"))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        # Adiciona todos os forms no contexto
        for name in self.get_form_classes():
            if f"form_{name}" not in kwargs:
                kwargs[f"form_{name}"] = self.get_form(name)
        # Adiciona campos básicos da ocorrência a serem mostrados
        kwargs["campos_ocorrencia"] = [
            "assunto",
            "casa_legislativa",
            "categoria",
            "descricao",
            "data_criacao",
            "data_modificacao",
        ]
        kwargs["list_filter"] = self.list_filter
        return super().get_context_data(**kwargs)


class OficinaChangeView(BaseOcorrenciaChangeView):
    template_name = "ocorrencias/oficina/painel_oficina_detail.html"
    form_classes = {"oficina": AutorizaOficinaForm}
    success_url_name = "ocorrencias_painel_oficina"

    def form_oficina_valid(self, form):
        ocorrencia = form.instance
        dados = form.cleaned_data
        total = 0
        for tipo_evento in dados["oficinas"]:
            evento = Evento(
                tipo_evento=tipo_evento,
                nome=_(
                    f"{tipo_evento.nome} na {ocorrencia.casa_legislativa.nome}"
                ),
                descricao=_(
                    f"{tipo_evento.nome} na {ocorrencia.casa_legislativa.nome}, oriunda da Ocorrência #{ocorrencia.id}"
                ),
                virtual=dados["virtual"],
                solicitante=ocorrencia.casa_legislativa.presidente.nome_completo
                if ocorrencia.casa_legislativa.presidente
                else "",
                num_processo=ocorrencia.processo_sigad,
                data_pedido=ocorrencia.data_criacao,
                solicitacao=ocorrencia,
                data_inicio=dados["data_inicio"],
                data_termino=dados["data_termino"],
                casa_anfitria=ocorrencia.casa_legislativa,
                municipio=ocorrencia.casa_legislativa.municipio,
                status=Evento.STATUS_PREVISTO,
            )
            evento.save()
            total += 1
        messages.info(self.request, _(f"{total} evento(s) criado(s)"))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ocorrencia = self.get_object()
        infos = ocorrencia.infos["solicita_oficinas"]
        senadores = Senador.objects.filter(id__in=infos["senadores"])
        context = super().get_context_data(**kwargs)
        context["senadores"] = senadores
        return context


class ConvenioChangeView(BaseOcorrenciaChangeView):
    template_name = "ocorrencias/convenio/painel_convenio_detail.html"
    success_url_name = "ocorrencias_painel_convenio"

    def post(self, request, *args, **kwargs):
        self.list_filter = request.GET.get("list_filter", "")
        if (
            "apply_casa" in request.POST
            or "apply_presidente" in request.POST
            or "apply_contato" in request.POST
        ):
            self.apply_changes(request)
            return HttpResponseRedirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ocorrencia = self.get_object()
        context = super().get_context_data(**kwargs)
        solicitacao = (
            ocorrencia.infos["solicita_convenio"]
            if ocorrencia.infos and "solicita_convenio" in ocorrencia.infos
            else {}
        )
        if not "aplicados" in solicitacao:
            solicitacao["aplicados"] = []

        context["infos"] = solicitacao
        context["casa"] = ocorrencia.casa_legislativa
        context["novo_presidente"] = (
            get_object_or_404(Parlamentar, id=solicitacao["presidente"]["id"])
            if "presidente" in solicitacao
            else None
        )
        context["contato"] = (
            ocorrencia.casa_legislativa.contato_interlegis or Funcionario()
        )
        return context

    def apply_changes(self, request):
        ocorrencia = self.get_object()
        solicitacao = (
            ocorrencia.infos["solicita_convenio"]
            if ocorrencia.infos and "solicita_convenio" in ocorrencia.infos
            else {}
        )
        casa = ocorrencia.casa_legislativa
        novo_presidente = (
            get_object_or_404(Parlamentar, id=solicitacao["presidente"]["id"])
            if "presidente" in solicitacao
            else None
        )
        contato = casa.contato_interlegis or Funcionario(
            casa_legislativa=casa, setor="contato_interlegis"
        )

        if not "aplicados" in solicitacao:
            solicitacao["aplicados"] = []

        if (
            "apply_casa" in request.POST
            and "casa_legislativa" in solicitacao
            and not "casa_legislativa" in solicitacao["aplicados"]
        ):
            if ocorrencia.casa_foto:
                casa.foto = ocorrencia.casa_foto
            if ocorrencia.casa_brasao:
                casa.brasao = ocorrencia.casa_brasao
            bound_copy(casa, solicitacao["casa_legislativa"])
            casa.save()
            solicitacao["aplicados"].append("casa_legislativa")
            ocorrencia.infos = {"solicita_convenio": solicitacao}
            ocorrencia.save()
            messages.info(request, _("Dados da casa aplicados com sucesso"))
            return
        if (
            "apply_presidente" in request.POST
            and "presidente" in solicitacao
            and "presidente" not in solicitacao["aplicados"]
        ):
            if novo_presidente is None:
                messages.error(
                    request,
                    _(
                        "A casa não possui parlamentares - impossível aplicar "
                        "os dados de presidente"
                    ),
                )
                return
            bound_copy(novo_presidente, solicitacao["presidente"], ["id"])
            novo_presidente.save()
            solicitacao["aplicados"].append("presidente")
            ocorrencia.infos = {"solicita_convenio": solicitacao}
            ocorrencia.save()
            messages.info(
                request, _("Dados do presidente aplicados com sucesso")
            )
            return
        if (
            "apply_contato" in request.POST
            and "contato" in solicitacao
            and "contato" not in solicitacao["aplicados"]
        ):
            bound_copy(contato, solicitacao["contato"])
            contato.save()
            solicitacao["aplicados"].append("contato")
            ocorrencia.infos = {"solicita_convenio": solicitacao}
            ocorrencia.save()
            messages.info(
                request, _("Dados do contato Interlegis aplicados com sucesso")
            )


################################################################################
# Views para site público - acesso dos contatos Interlegis                     #
################################################################################


class BaseSelecionaCasaView(TemplateView):
    template_name = "public/ocorrencias/seleciona_casa.html"
    title = _("Selecionar Casa Legislativa")
    summary = _("Selecione uma Casa Legislativa")
    success_url = reverse_lazy("ocorrencias:ocorrencia_seleciona_casa")
    parameter_name = "casa_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.title,
                "summary": self.summary,
                "success_url": self.success_url,
                "parameter_name": self.parameter_name,
            }
        )
        return context


class OficinaSelecionaCasaView(BaseSelecionaCasaView):
    title = _("Solicitar oficinas / treinamentos")
    summary = _(
        """
        As Casas Legislativas podem solicitar oficinas, treinamentos e encontros
        Interlegis, tanto na modalidade presencial, quanto à distância. Para
        efetuar a solicitação, identifique primeiramente sua Casa Legislativa
        (na caixa de pesquisa abaixo), e então preencha o formulário de
        solicitação de oficinas que será apresentado em seguida. Um ofício de
        solicitação será gerado. Você deverá fazer download desse ofício,
        solicitar que o Presidente da Casa o assine, e então, deverá fazer
        upload da imagem do ofício assinado, para que o Interlegis possa dar
        seguimento ao atendimento de sua demanda. Assim que recebermos o ofício,
        entraremos em contato com a Casa Legislativa para definirmos as melhores
        datas e acertarmos os diversos detalhes para a realização do evento.
        """
    )
    success_url = reverse_lazy("ocorrencias:solicita_oficina_create")


class ConvenioSelecionaCasaView(BaseSelecionaCasaView):
    title = _("Solicitar convênio / Acordo de Cooperação Técnica")
    summary = _(
        """
        <p>Para que uma Casa Legislativa possa utilizar, gratuitamente, os
        serviços do Interlegis / Senado Federal, é necessário formalizar um
        convênio, na forma de um Acordo de Cooperação Técnica (ACT), conforme
        a Lei Nº 14.133/2021 e a Lei Nº 8.666/1993.</p>
        <p>Para solicitar o ACT, serão necessárias as seguintes informações:</p>
        <ul>
          <li>Dados cadastrais da Casa Legislativa, como CNPJ, endereço, e-mail,
          telefone.</li>
          <li>Dados cadastrais do Presidente, como nome, CPF, identidade,
          e-mail, telefone, redes sociais.</li>
          <li>Designação de um servidor como Contato Interlegis.</li>
        </ul>
        """
    )
    success_url = reverse_lazy("ocorrencias:solicita_convenio")


class OcorrenciaListView(
    ContatoInterlegisViewMixin, LoginRequiredMixin, ListView
):
    model = Ocorrencia
    paginate_by = 100
    template_name = "public/ocorrencias/ocorrencia_list.html"

    def get_queryset(self):
        casa = self.get_casa()
        statuses = self.request.GET.getlist(
            "status", [Ocorrencia.STATUS_ABERTO, Ocorrencia.STATUS_REABERTO]
        )
        if casa:
            return casa.ocorrencia_set.exclude(interno=True).filter(
                status__in=statuses
            )
        else:
            return Ocorrencia.objects.none()

    def post(self, request):
        casa = self.get_casa()
        ocorrencia = casa.ocorrencia_set.get(
            id=request.POST.get("ocorrencia_id", None)
        )
        nome = request.user.get_full_name()
        url = reverse("ocorrencias:ocorrencia_listview")
        url = f"{url}#ocorrencia-{ocorrencia.id}"

        if "comentario_save" in request.POST:
            usuario = (
                request.user.servidor
                if request.user.servidor
                else Servidor.objects.get(sigi=True)
            )
            comentario = Comentario(ocorrencia=ocorrencia, usuario=usuario)
            form = ComentarioForm(request.POST, instance=comentario)
            if form.is_valid():
                comentario = form.save(commit=False)
                comentario.descricao = f"({nome}): {comentario.descricao}"
                comentario.save()
                messages.info(request, _("Comentário salvo"))
            else:
                messages.error(request, _("Corrija os erros"))
        elif "anexo_save" in request.POST:
            anexo = Anexo(ocorrencia=ocorrencia)
            form = AnexoForm(request.POST, request.FILES, instance=anexo)
            if form.is_valid():
                anexo = form.save()
                messages.info(request, _("Anexo salvo"))
            else:
                messages.error(request, _("Corrija os erros"))

        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        selected_status = self.request.GET.getlist(
            "status", [Ocorrencia.STATUS_ABERTO, Ocorrencia.STATUS_REABERTO]
        )
        context = super().get_context_data(**kwargs)
        context["comentario_form"] = ComentarioForm()
        context["anexo_form"] = AnexoForm()
        context["statuses"] = Ocorrencia.STATUS_CHOICES
        context["selected_status"] = list(map(int, selected_status))
        return context


class SolicitaConvenioCreateView(ContatoInterlegisViewMixin, UpdateView):
    ANEXO_DESCRICAO = _("Solicitação de convenio assinada")

    model = Ocorrencia
    template_name = "public/ocorrencias/solicita_convenio_create.html"
    form_classes = {
        "casa": CasaForm,
        "presidente": PresidenteForm,
        "contato": ContatoForm,
        "documentos": DocumentoForm,
        "resumo": ComentarioForm,
    }

    def get(self, request, *args, **kwargs):
        self.tab = kwargs.get("tab", None)
        if self.tab is None:
            if self.pk_url_kwarg in kwargs:
                self.set_instances()
                self.tab = (
                    "casa"
                    if "casa_legislativa" not in self.infos
                    else "presidente"
                    if "presidente" not in self.infos
                    else "contato"
                    if "contato" not in self.infos
                    else "documentos"
                    if "documento" in self.infos
                    else "resumo"
                )
            else:
                return self.cria_solicitacao(request, *args, **kwargs)
        self.set_instances()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.tab = request.POST.get("tab", None)
        ocorrencia = self.get_object()
        if self.tab is None:
            messages.error(request, "Erro na página. Dados não foram salvos")
            return HttpResponseRedirect(
                reverse(
                    "ocorrencias:solicita_convenio",
                    kwargs={"pk": ocorrencia.id},
                )
            )
        self.set_instances()
        return super().post(request, *args, **kwargs)

    def get_success_url(self, tab=None):
        obj = self.get_object()
        if tab is None:
            tab = self.tab
        return reverse(
            "ocorrencias:solicita_convenio", kwargs={"pk": obj.id, "tab": tab}
        )

    def get_form_class(self):
        return self.form_classes[self.tab]

    def form_valid(self, form):
        if hasattr(self, f"form_valid_{self.tab}"):
            form_valid_function = getattr(self, f"form_valid_{self.tab}")
            next_tab = form_valid_function(form)
            self.object.infos = {"solicita_convenio": self.infos}
            self.object.save()
            if {"casa_legislativa", "presidente", "contato"}.issubset(
                self.infos
            ) and self.tab in ["casa", "presidente", "contato"]:
                if "documento" in self.infos:
                    del self.infos["documento"]
                self.object.infos = {"solicita_convenio": self.infos}
                self.object.save()
                self.set_instances()
                self.object.anexo_set.all().delete()
                projeto = self.object.categoria.projeto
                oficio = Anexo(
                    ocorrencia=self.object,
                    descricao=f"Solicitação de {projeto.sigla}",
                )
                oficio.arquivo.name = (
                    f"{Anexo.arquivo.field.upload_to}/"
                    f"solicitacao_{projeto.sigla}_{self.casa.get_sigla()}.pdf"
                )
                projeto.gerar_oficio(
                    oficio.arquivo,
                    self.casa,
                    self.presidente,
                    self.contato,
                    self.request.build_absolute_uri("/"),
                )
                oficio.save()
                minuta = Anexo(
                    ocorrencia=self.object,
                    descricao=f"Minuta de {projeto.sigla}",
                )
                minuta.arquivo.name = (
                    f"{Anexo.arquivo.field.upload_to}/"
                    f"minuta_{projeto.sigla}_{self.casa.get_sigla()}.docx"
                )
                projeto.gerar_minuta(
                    minuta.arquivo.path,
                    self.casa,
                    self.presidente,
                    self.contato,
                )
                minuta.save()
            return HttpResponseRedirect(self.get_success_url(tab=next_tab))
        else:
            raise ImproperlyConfigured(f"No form_valid_{self.tab} implemented")

    def get_prefix(self):
        return self.tab

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.tab == "casa":
            kwargs["instance"] = self.casa
        elif self.tab == "presidente":
            if "presidente" in self.infos:
                prefix = kwargs["prefix"]
                bounds = {
                    f"{prefix}-{key}": value
                    for key, value in self.infos["presidente"].items()
                    if key != "id"
                }
                bounds[f"{prefix}-parlamentar"] = self.presidente
                kwargs["data"] = bounds
            kwargs["instance"] = self.presidente
        elif self.tab == "contato":
            kwargs["instance"] = self.contato
        elif self.tab == "documentos":
            kwargs["instance"] = Anexo(
                ocorrencia=self.object, descricao=self.ANEXO_DESCRICAO
            )
        elif self.tab == "resumo":
            if self.object.status not in [
                Ocorrencia.STATUS_ABERTO,
                Ocorrencia.STATUS_REABERTO,
            ]:
                status = Ocorrencia.STATUS_REABERTO
            else:
                status = None
            kwargs["instance"] = Comentario(
                ocorrencia=self.object,
                usuario=self.object.servidor_registro,
                novo_status=status,
            )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["infos"] = self.infos
        context["tab_name"] = self.tab
        return context

    def set_instances(self):
        self.object = self.get_object()
        self.casa = self.object.casa_legislativa
        self.infos = (
            self.object.infos["solicita_convenio"]
            if self.object.infos and "solicita_convenio" in self.object.infos
            else {}
        )
        self.presidente = self.casa.presidente or (
            Parlamentar.objects.get(id=self.infos["presidente"]["id"])
            if "presidente" in self.infos
            else Parlamentar(casa_legislativa=self.casa)
        )
        self.contato = self.casa.contato_interlegis or Funcionario(
            casa_legislativa=self.casa, setor="contato_interlegis"
        )
        if self.object.casa_foto:
            self.casa.foto = self.object.casa_foto
        if self.object.casa_brasao:
            self.casa.brasao = self.object.casa_brasao
        if "casa_legislativa" in self.infos:
            bound_copy(self.casa, self.infos["casa_legislativa"])
        if "presidente" in self.infos:
            bound_copy(self.presidente, self.infos["presidente"], ["id"])
        if "contato" in self.infos:
            bound_copy(self.contato, self.infos["contato"])

    def cria_solicitacao(self, request, *args, **kwargs):
        casa_id = request.GET.get("casa_id", None)
        if casa_id is None:
            messages.error(
                request,
                _("Selecione uma casa legislativa para iniciar o processo"),
            )
            return redirect(
                reverse(
                    "ocorrencias:ocorrencia_convenio_seleciona_casa",
                )
            )
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
            status__in=[
                Ocorrencia.STATUS_ABERTO,
                Ocorrencia.STATUS_REABERTO,
            ],
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
                infos={"solicita_convenio": {}},
            )
            ocorrencia.save()
        return redirect(
            reverse(
                "ocorrencias:solicita_convenio",
                kwargs={"pk": ocorrencia.id, "tab": "casa"},
            )
        )

    def form_valid_casa(self, form):
        cleaned = form.cleaned_data.copy()
        foto = cleaned.pop("foto")
        brasao = cleaned.pop("brasao")
        if "foto" in form.changed_data:
            if foto == False:
                if self.object.casa_foto:
                    self.object.casa_foto.delete(save=True)
            else:
                self.object.casa_foto = foto
        if "brasao" in form.changed_data:
            if brasao == False:
                if self.object.casa_brasao:
                    self.object.casa_brasao.delete(save=True)
            else:
                self.object.casa_brasao = brasao

        self.infos["casa_legislativa"] = cleaned
        return "presidente"

    def form_valid_presidente(self, form):
        cleaned = form.cleaned_data.copy()
        presidente = cleaned.pop("parlamentar")
        cleaned["id"] = presidente.id
        self.infos["presidente"] = cleaned
        return "contato"

    def form_valid_contato(self, form):
        self.infos["contato"] = form.cleaned_data.copy()
        return "documentos"

    def form_valid_documentos(self, form):
        documento = form.save()
        self.infos["documento"] = {"id": documento.id}
        return "resumo"

    def form_valid_resumo(self, form):
        comentario = form.save(commit=False)
        comentario.ocorrencia = self.object
        comentario.usuario = self.object.servidor_registro
        if self.object.status not in [
            Ocorrencia.STATUS_ABERTO,
            Ocorrencia.STATUS_REABERTO,
        ]:
            comentario.novo_status = Ocorrencia.STATUS_REABERTO
        comentario.save()
        return "resumo"


class SolicitaOficinaCreateView(ContatoInterlegisViewMixin, CreateView):
    model = Ocorrencia
    form_class = SolicitaTreinamentoForm
    template_name = "public/ocorrencias/solicita_treinamento_create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        senadores = Senador.objects.filter(uf=self.get_casa().municipio.uf)
        kwargs.update({"senadores": senadores})
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "senadores": Senador.objects.filter(
                    uf=self.get_casa().municipio.uf
                )
            }
        )
        return initial

    def get(self, request, *args, **kwargs):
        casa_id = request.GET.get("casa_id", None)
        if request.user.is_anonymous and casa_id is None:
            return HttpResponseRedirect(
                reverse("ocorrencias:ocorrencia_oficina_seleciona_casa")
            )

        if casa_id:
            self.request.session["casa_id"] = casa_id

        ocorrencia = Ocorrencia.objects.filter(
            casa_legislativa=self.get_casa(),
            status__in=[
                Ocorrencia.STATUS_ABERTO,
                Ocorrencia.STATUS_REABERTO,
            ],
            categoria__tipo="E",
        ).first()
        if ocorrencia:
            messages.info(
                request,
                _("Existe esta solicitação de treinamento em andamento."),
            )
            return HttpResponseRedirect(
                reverse(
                    "ocorrencias:solicita_oficina_view",
                    kwargs={"pk": ocorrencia.id},
                )
            )
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "ocorrencias:solicita_oficina_view",
            kwargs={"pk": self.object.id},
        )

    def form_valid(self, form):
        casa = self.get_casa()
        contato = self.get_contato() or Funcionario(nome="NÃO IDENTIFICADO")
        self.object = form.save(commit=False)
        data = form.cleaned_data
        oficinas = form.cleaned_data["oficinas"]
        data["oficinas"] = list(oficinas.values_list("id", flat=True))
        senadores = form.cleaned_data["senadores"]
        data["senadores"] = list(senadores.values_list("id", flat=True))
        self.object.casa_legislativa = casa
        self.object.categoria = Categoria.objects.filter(tipo="E").first()
        self.object.tipo_contato = TipoContato.objects.filter(
            ind_site=True
        ).first()
        self.object.assunto = _("Solicitação de oficinas Interlegis")
        self.object.interno = False
        self.object.descricao = _(
            f"O Contato Interlegis { contato.nome } solicita a realização das "
            f"seguites oficinas na { casa }, conforme ofício anexo:"
        )
        self.object.descricao = self.object.descricao + ", ".join(
            o.nome for o in oficinas
        )
        self.object.servidor_registro = Servidor.objects.get(sigi=True)
        self.object.infos = {"solicita_oficinas": data}
        self.object.save()
        oficio = Anexo(
            ocorrencia=self.object,
            descricao=_("Oficio de solicitação de oficinas"),
        )
        oficio.arquivo.name = (
            f"{Anexo.arquivo.field.upload_to}/solicitacao_oficinas.pdf"
        )
        html = render_to_string(
            "public/ocorrencias/oficio_oficina_pdf.html",
            context={
                "casa": casa,
                "ocorrencia": self.object,
                "oficinas": oficinas,
            },
        )
        pdf = HTML(
            string=html,
            url_fetcher=django_url_fetcher,
            encoding="utf-8",
            base_url=self.request.build_absolute_uri("/"),
        )
        if not oficio.arquivo.closed:
            oficio.arquivo.close()
        oficio.arquivo.open(mode="wb")
        pdf.write_pdf(target=oficio.arquivo)
        oficio.arquivo.flush()
        oficio.save()

        return super().form_valid(form)


class SolicitaOficinaView(ContatoInterlegisViewMixin, UpdateView):
    model = Anexo
    form_class = DocumentoForm
    template_name = "public/ocorrencias/solicita_treinamento_view.html"

    def get_success_url(self):
        return (
            reverse("ocorrencias:ocorrencia_listview")
            + f"#{self.object.ocorrencia.id}"
        )

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )
        try:
            ocorrencia = Ocorrencia.objects.get(pk=pk)
        except Ocorrencia.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": Ocorrencia._meta.verbose_name}
            )
        return Anexo(
            ocorrencia=ocorrencia,
            descricao=_("Oficio de solicitação de oficinas assinado"),
        )

    def get_casa(self):
        if self.request.user.is_anonymous:
            return self.get_object().ocorrencia.casa_legislativa
        else:
            return super().get_casa()

    def form_valid(self, form):
        response = super().form_valid(form)
        anexo = self.object
        casa = self.get_casa()
        senadores = anexo.ocorrencia.get_infos_senadores()
        if casa.presidente and casa.presidente.email:
            sender = {
                "nome": casa.presidente.nome_completo,
                "email": casa.presidente.email,
                "funcao": _("Presidente"),
            }
        elif casa.contato_interlegis and casa.contato_interlegis.email:
            sender = {
                "nome": casa.contato_interlegis.nome,
                "email": casa.contato_interlegis.email,
                "funcao": casa.contato_interlegis,
            }
        else:
            sender = {
                "nome": "",
                "email": settings.DEFAULT_FROM_EMAIL,
                "funcao": _("Presidente"),
            }
        email = EmailMessage(
            subject=_("Solicitação de oficinas Interlegis"),
            from_email=sender["email"],
            reply_to=[sender["email"]],
        )
        if sender["email"] != settings.DEFAULT_FROM_EMAIL:
            email.cc = [sender["email"]]
        email.content_subtype = "html"
        email.attach_file(anexo.arquivo.path)
        for senador in senadores:
            email.to = [senador.email]
            email.body = render_to_string(
                "ocorrencias/oficina/email_senador.html",
                context={"casa": casa, "senador": senador, "sender": sender},
            )
            email.send()

        messages.info(
            self.request,
            _(
                "Email enviado para os senadores "
                + ", ".join([s.nome_parlamentar for s in senadores])
            ),
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ocorrencia"] = self.get_object().ocorrencia
        return context
