from django.contrib import admin
from django.utils.translation import gettext as _
from sigi.apps.servidores.models import Servidor
from sigi.apps.convenios.models import Projeto
from sigi.apps.servicos.models import TipoServico


class GerentesInterlegisFilter(admin.filters.RelatedFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gerentes = Servidor.objects.exclude(casas_que_gerencia=None).order_by(
            "nome_completo"
        )
        self.lookup_choices = [(x.id, x) for x in gerentes]


class ConvenioFilter(admin.SimpleListFilter):
    title = _("Tipo de convênio")
    parameter_name = "convenio"

    def lookups(self, request, model_admin):
        return (
            ("SC", _("Sem nenhum convênio")),
            ("CC", _("Com algum convênio")),
        ) + tuple([(p.pk, p.sigla) for p in Projeto.objects.all()])

    def queryset(self, request, queryset):
        if self.value() is not None:
            if self.value() == "SC":
                queryset = queryset.filter(convenio=None)
            elif self.value() == "CC":
                queryset = queryset.exclude(convenio=None)
            else:
                queryset = queryset.filter(convenio__projeto_id=self.value())

        return queryset.distinct("municipio__uf__nome", "nome")


class ExcluirConvenioFilter(admin.SimpleListFilter):
    title = _("Excluir convênio da pesquisa")
    parameter_name = "excluir_convenio"

    def lookups(self, request, model_admin):
        return tuple([(p.pk, p.sigla) for p in Projeto.objects.all()])

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            queryset = queryset.exclude(
                convenio__projeto_id=self.value()
            ).distinct("municipio__uf__nome", "nome")
        return queryset


class ServicoFilter(admin.SimpleListFilter):
    title = _("Serviço")
    parameter_name = "servico"

    def lookups(self, request, model_admin):
        return (
            ("SS", _("Sem nenhum serviço")),
            ("CS", _("Com algum serviço")),
            ("CH", _("Com algum serviço de hospedagem")),
            ("CR", _("Apenas serviço de registro")),
        ) + tuple([(p.pk, p.nome) for p in TipoServico.objects.all()])

    def queryset(self, request, queryset):
        if self.value() is not None:
            if self.value() == "SS":
                queryset = queryset.filter(servico=None)
            elif self.value() == "CS":
                queryset = queryset.exclude(servico=None).filter(
                    servico__data_desativacao__isnull=True
                )
            elif self.value() == "CR":
                queryset = queryset.exclude(
                    servico__tipo_servico__modo="H"
                ).exclude(servico=None)
            elif self.value() == "CH":
                queryset = queryset.filter(
                    servico__tipo_servico__modo="H",
                    servico__data_desativacao__isnull=True,
                )
            else:
                queryset = queryset.filter(
                    servico__tipo_servico_id=self.value()
                )

        return queryset.distinct("municipio__uf__nome", "nome")
