from requests import options
from django import forms
from django.utils.translation import gettext as _
from sigi.apps.contatos.models import UnidadeFederativa


class ImportForm(forms.Form):
    CODIFICACAO_CHOICES = (
        ("iso8859-1", _("LATIN 1 (iso-8859-1)")),
        ("utf-8", _("UTF-8")),
    )
    UF_CHOICES = [
        ("BR", _("Todo o Brasil")),
    ] + [(uf.sigla, uf.nome) for uf in UnidadeFederativa.objects.all()]
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
    uf_importar = forms.ChoiceField(
        label=_("Unidade Federativa"), choices=UF_CHOICES
    )
