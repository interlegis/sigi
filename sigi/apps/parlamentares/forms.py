from requests import options
from django import forms
from django.utils.translation import gettext as _
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.parlamentares.models import Parlamentar


class ImportForm(forms.Form):
    CODIFICACAO_CHOICES = (
        ("iso8859-1", _("LATIN 1 (iso-8859-1)")),
        ("utf-8", _("UTF-8")),
    )
    TIPO_CHOICES = [
        ("V", _("Vereador")),
        ("D", _("Deputado Estadual")),
    ]
    codificacao = forms.ChoiceField(
        label=_("Codificação de caracteres"),
        choices=CODIFICACAO_CHOICES,
        help_text=_(
            "Verifique no PDF do TSE a codificação de caracteres dos "
            "arquivos"
        ),
    )
    arquivo_tse = forms.FileField(label=_("Arquivo do TSE"), required=False)
    arquivo_redes = forms.FileField(
        label=_("Arquivo de redes sociais"), required=False
    )
    arquivo_fotos = forms.FileField(label=_("Zip das fotos"), required=False)
    tipo_candidatos = forms.ChoiceField(
        label=_("Tipo de candidatos"), choices=TIPO_CHOICES
    )
    suplentes = forms.BooleanField(
        label=_("Importar suplentes"), required=False
    )
    uf_importar = forms.ChoiceField(label=_("Unidade Federativa"), choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["uf_importar"].choices = [
            ("BR", _("Todo o Brasil")),
        ] + [(uf.sigla, uf.nome) for uf in UnidadeFederativa.objects.all()]


class ParlamentarForm(forms.ModelForm):
    class Meta:
        model = Parlamentar
        fields = [
            "foto",
            "nome_completo",
            "nome_parlamentar",
            "partido",
            "ano_eleicao",
            "status_mandato",
            "presidente",
            "data_nascimento",
            "cpf",
            "identidade",
            "telefones",
            "email",
            "redes_sociais",
        ]
