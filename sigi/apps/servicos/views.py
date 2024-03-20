import csv
from django.db.models import Q, Prefetch, Count
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView
from import_export import resources
from import_export.fields import Field
from sigi.apps.casas.models import Orgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.convenios.models import Convenio
from sigi.apps.eventos.models import Evento, TipoEvento
from sigi.apps.servicos.models import Servico
from sigi.apps.utils import to_ascii


class ServicoResource(resources.ModelResource):
    telefone = Field(column_name="casa_legislativa__telefone")

    class Meta:
        model = Servico
        fields = [
            "casa_legislativa__cnpj",
            "casa_legislativa__nome",
            "casa_legislativa__tipo__nome",
            "casa_legislativa__logradouro",
            "casa_legislativa__bairro",
            "casa_legislativa__cep",
            "casa_legislativa__municipio__nome",
            "casa_legislativa__municipio__uf__sigla",
            "casa_legislativa__email",
            "telefone",
            "tipo_servico__nome",
            "data_ativacao",
            "url",
        ]
        export_order = fields

        def dehydrate_telefone(self, servico):
            return servico.casa_legislativa.telefone


class CasasAtendidasListView(ListView):
    model = Orgao
    template_name = "servicos/casas_atendidas.html"
    paginate_by = 100

    def get_queryset(self):
        param = self.kwargs["param"]
        search_param = self.request.GET.get("search", None)

        sq_servicos = Servico.objects.filter(data_desativacao=None)
        sq_eventos = (
            Evento.objects.exclude(data_inicio=None)
            .exclude(data_termino=None)
            .exclude(tipo_evento__categoria=TipoEvento.CATEGORIA_VISITA)
            .filter(status=Evento.STATUS_REALIZADO)
        )
        queryset = super().get_queryset()
        queryset = (
            queryset.filter(tipo__legislativo=True)
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
                Prefetch(
                    "servico_set", queryset=sq_servicos, to_attr="servicos"
                ),
                Prefetch("evento_set", queryset=sq_eventos, to_attr="eventos"),
                Prefetch(
                    "convenio_set",
                    queryset=Convenio.objects.select_related("projeto"),
                    to_attr="convenios",
                ),
            )
        ).order_by("municipio__uf__nome", "tipo__nome", "nome")

        if search_param:
            filter = [
                Q(search_text__icontains=to_ascii(t.lower()))
                for t in search_param.split()
            ]
            queryset = queryset.filter(*filter)
        if param.isdigit():
            queryset = queryset.filter(id=param)
        elif param != "_all_":
            queryset = queryset.filter(municipio__uf__sigla=param)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        param = self.kwargs["param"]
        context["tot_orgaos"] = self.get_queryset().count()
        context["mapa_valores"] = dict(
            Orgao.objects.exclude(municipio__uf__sigla="ZZ")
            .exclude(servico=None, evento=None)
            .exclude(~Q(servico__data_desativacao=None))
            .filter(tipo__legislativo=True)
            .order_by("municipio__uf__sigla")
            .values_list("municipio__uf__sigla")
            .annotate(Count("id", distinct=True))
        )
        context["regioes"] = [
            (
                regiao,
                UnidadeFederativa.objects.filter(regiao=r).exclude(sigla="ZZ"),
            )
            for r, regiao in UnidadeFederativa.REGIAO_CHOICES
        ]
        context["search_param"] = self.request.GET.get("search", None)
        if param != "_all_" and not param.isdigit():
            context["uf"] = UnidadeFederativa.objects.get(sigla=param)
        return context

    def render_to_response(self, context, **response_kwargs):
        format = self.request.GET.get("format", "html")
        if format == "csv":
            orgaos = self.get_queryset().values_list("id")
            servicos = Servico.objects.filter(
                data_desativacao=None, casa_legislativa_id__in=orgaos
            )
            data = ServicoResource().export(servicos)
            return HttpResponse(
                data.csv,
                content_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment;filename="orgaos_interlegis.csv"'
                },
            )
        return super().render_to_response(context, **response_kwargs)

    @xframe_options_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
