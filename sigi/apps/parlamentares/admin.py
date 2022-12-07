import json
import tablib
from django.db.models import Q
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from import_export import resources
from import_export.admin import ImportMixin
from import_export.formats.base_formats import CSV
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.parlamentares.jobs import import_path, json_path
from sigi.apps.parlamentares.models import Partido, Parlamentar, Senador
from sigi.apps.parlamentares.forms import ImportForm
from sigi.apps.utils.filters import AlphabeticFilter
from sigi.apps.utils.mixins import (
    ReturnMixin,
    ImportCartExportMixin,
    CartExportMixin,
    LabeledResourse,
)


class ParlamentarResource(LabeledResourse):
    class Meta:
        model = Parlamentar
        fields = (
            "casa_legislativa__nome",
            "casa_legislativa__municipio__uf__sigla",
            "partido__legenda",
            "partido__sigla",
            "partido__nome",
            "presidente",
            "nome_completo",
            "nome_parlamentar",
            "data_nascimento",
            "cpf",
            "identidade",
            "telefones",
            "email",
            "redes_sociais",
            "ult_alteracao",
            "observacoes",
        )
        export_order = fields


class SenadorImportResource(resources.ModelResource):
    uf = resources.Field(
        attribute="uf",
        column_name="/ListaParlamentarEmExercicio/Parlamentares/Parlamentar/IdentificacaoParlamentar/UfParlamentar",
    )
    partido = resources.Field(
        attribute="partido",
        column_name="/ListaParlamentarEmExercicio/Parlamentares/Parlamentar/IdentificacaoParlamentar/SiglaPartidoParlamentar",
    )
    codigo = resources.Field(
        attribute="codigo",
        column_name="/ListaParlamentarEmExercicio/Parlamentares/Parlamentar/IdentificacaoParlamentar/CodigoParlamentar",
    )
    nome_parlamentar = resources.Field(
        attribute="nome_parlamentar",
        column_name="/ListaParlamentarEmExercicio/Parlamentares/Parlamentar/IdentificacaoParlamentar/NomeParlamentar",
    )
    nome_completo = resources.Field(
        attribute="nome_completo",
        column_name="/ListaParlamentarEmExercicio/Parlamentares/Parlamentar/IdentificacaoParlamentar/NomeCompletoParlamentar",
    )
    sexo = resources.Field(
        attribute="sexo",
        column_name="/ListaParlamentarEmExercicio/Parlamentares/Parlamentar/IdentificacaoParlamentar/SexoParlamentar",
    )
    forma_tratamento = resources.Field(
        attribute="forma_tratamento",
        column_name="/ListaParlamentarEmExercicio/Parlamentares/Parlamentar/IdentificacaoParlamentar/FormaTratamento",
    )
    email = resources.Field(
        attribute="email",
        column_name="/ListaParlamentarEmExercicio/Parlamentares/Parlamentar/IdentificacaoParlamentar/EmailParlamentar",
    )

    class Meta:
        import_id_fields = ["codigo"]
        model = Senador
        fields = (
            "uf",
            "partido",
            "codigo",
            "nome_parlamentar",
            "nome_completo",
            "sexo",
            "forma_tratamento",
            "email",
        )
        report_skipped = False
        skip_unchanged = True

    def __init__(self):
        super().__init__()
        self.partidos = {p.sigla.upper(): p for p in Partido.objects.all()}
        self.partidos.update({p.nome.upper(): p for p in Partido.objects.all()})
        self.ufs = {uf.sigla: uf for uf in UnidadeFederativa.objects.all()}

    def before_import_row(self, row, row_number=None, **kwargs):
        uf = self.fields["uf"].column_name
        partido = self.fields["partido"].column_name
        sexo = self.fields["sexo"].column_name
        if sexo in row:
            row[sexo] = row.get(sexo)[0]
        if uf in row and row.get(uf) != "":
            row[uf] = self.ufs.get(row.get(uf, "").upper())
        if partido in row and row.get(partido) != "":
            sigla_partido = row.get(partido, "")
            if sigla_partido == "S/Partido":
                sigla_partido = "SEM PARTIDO"
            row[partido] = self.partidos.get(sigla_partido.upper())
        return row

    def skip_row(self, instance, original):
        result = (
            not hasattr(instance, "uf") or not hasattr(instance, "email")
        ) or super().skip_row(instance, original)
        return result


class SemicolonCSV(CSV):
    def get_title(self):
        return "CSV do Senado"

    def create_dataset(self, in_stream, **kwargs):
        return tablib.import_set(in_stream, format="csv", delimiter=";")


class ParlamentarNomeCompletoFilter(AlphabeticFilter):
    title = _("Inicial do Nome Completo")
    parameter_name = "nome_completo"


@admin.register(Partido)
class PartidoAdmin(ImportCartExportMixin, admin.ModelAdmin):
    list_display = ("legenda", "nome", "sigla")
    search_fields = ("legenda", "nome", "sigla")


@admin.register(Parlamentar)
class ParlamentarAdmin(ReturnMixin, CartExportMixin, admin.ModelAdmin):
    resource_class = ParlamentarResource
    change_list_template = (
        "admin/parlamentares/parlamentar/cart/"
        "change_list_import_cart_export.html"
    )
    list_display = (
        "get_foto",
        "nome_completo",
        "casa_legislativa",
        "status_mandato",
        "get_uf",
        "partido",
    )
    list_filter = (
        "casa_legislativa__municipio__uf",
        ("casa_legislativa__tipo", admin.RelatedOnlyFieldListFilter),
        "partido",
        "status_mandato",
        "presidente",
        ParlamentarNomeCompletoFilter,
    )
    fieldsets = (
        (
            _("mandato"),
            {
                "fields": (
                    "casa_legislativa",
                    "ano_eleicao",
                    "partido",
                    "presidente",
                )
            },
        ),
        (
            _("dados pessoais"),
            {
                "fields": (
                    "nome_completo",
                    "nome_parlamentar",
                    "foto",
                    "data_nascimento",
                    "cpf",
                    "identidade",
                ),
            },
        ),
        (
            _("contatos"),
            {"fields": ("telefones", "email", "redes_sociais")},
        ),
    )
    autocomplete_fields = ("casa_legislativa", "partido")
    search_fields = (
        "nome_completo",
        "nome_parlamentar",
        "email",
        "casa_legislativa__search_text",
    )

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        my_urls = [
            path(
                "import/",
                self.admin_site.admin_view(self.import_action),
                name="%s_%s_import" % info,
            ),
            path(
                "import_result/",
                self.admin_site.admin_view(self.result_import_action),
                name="%s_%s_import_result" % info,
            ),
        ]
        return my_urls + urls

    @admin.display(
        description=_("UF"), ordering="casa_legislativa__municipio__uf__nome"
    )
    def get_uf(self, obj):
        return obj.casa_legislativa.municipio.uf.nome

    @mark_safe
    @admin.display(description=_("Foto"))
    def get_foto(self, obj):
        if obj.foto:
            return f'<img class="circle" src="{obj.foto.url}" style="width: 58px; height: 58px;"/>'
        else:
            return (
                '<i class="material-icons medium grey-text">account_circle</i>'
            )

    def import_action(self, request, *args, **kwargs):
        def save_file(uploaded, destination_path):
            with open(destination_path / uploaded.name, "wb") as dst_file:
                for chunck in uploaded:
                    dst_file.write(chunck)
                dst_file.flush()

        form = ImportForm(request.POST, request.FILES)
        context = {
            "opts": self.model._meta,
            "form": form,
            "last_result": import_path / "result.html",
        }
        if request.method == "POST" and form.is_valid():
            json_data = {
                "upload_time": timezone.localtime(),
                "user_id": request.user.id,
                "tipo_candidatos": form.cleaned_data["tipo_candidatos"],
                "suplentes": form.cleaned_data["suplentes"],
                "codificacao": form.cleaned_data["codificacao"],
                "sigla_uf": form.cleaned_data["uf_importar"],
            }
            if form.cleaned_data["arquivo_tse"]:
                save_file(form.cleaned_data["arquivo_tse"], import_path)
                json_data["resultados"] = form.cleaned_data["arquivo_tse"].name
            if form.cleaned_data["arquivo_redes"]:
                save_file(form.cleaned_data["arquivo_redes"], import_path)
                json_data["redes_sociais"] = form.cleaned_data[
                    "arquivo_redes"
                ].name
            if form.cleaned_data["arquivo_fotos"]:
                save_file(form.cleaned_data["arquivo_fotos"], import_path)
                json_data["fotos"] = form.cleaned_data["arquivo_fotos"].name
            json_path.write_text(json.dumps(json_data, default=str))
            return redirect(
                reverse("admin:%s_%s_import_result" % self.get_model_info())
            )
        return render(request, "parlamentares/import.html", context)

    def result_import_action(self, request, *args, **kwargs):
        context = {"opts": self.model._meta}
        return render(request, "parlamentares/import_result.html", context)


@admin.register(Senador)
class SenadorAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = SenadorImportResource
    list_display = ("nome_parlamentar", "uf", "partido")
    list_filter = ("uf", "partido", "sexo")
    search_fields = (
        "nome_parlamentar",
        "nome",
        "uf__sigla",
        "uf__nome",
        "partido__sigla",
        "partido__nome",
    )
    autocomplete_fields = ("partido",)

    def get_import_formats(self):
        return [SemicolonCSV]
