from django import forms
from django.utils.translation import gettext_lazy as _


class AppConfigForm(forms.Form):
    form_title = _("Definições para convênios")
    form_subtitle = _("Importação do Gescon")
    url_gescon = forms.URLField(
        required=True,
        label=_("Webservice Gescon"),
        initial=(
            "https://adm.senado.gov.br/gestao-contratos/api/contratos"
            "/busca?subespecie={s}"
        ),
        help_text=_(
            "Informe o ponto de consulta do webservice do Gescon, "
            "inclusive com a querystring. No ponto onde deve ser "
            "inserida a sigla da subespecie do contrato, use a "
            "marcação {s}.<br/><strong>Por exemplo:</strong> "
            "https://adm.senado.gov.br/gestao-contratos/api/contratos"
            "/busca?subespecie=<strong>{s}</strong>"
        ),
    )
    subespecies = forms.CharField(
        required=True,
        label=_("Subespécies"),
        initial="AC=ACT\nTC=TC",
        help_text=_(
            "Informe as siglas das subespécies de contratos que "
            "devem ser pesquisados no Gescon com a sigla "
            "correspondente do projeto no SIGI. Coloque um par de "
            "siglas por linha, no formato SIGLA_GESTON=SIGLA_SIGI. "
            "As siglas não encontradas serão ignoradas."
        ),
        widget=forms.Textarea(),
    )
    palavras = forms.CharField(
        required=True,
        label=_("Palavras de filtro"),
        initial="ILB\nINTERLEGIS\nSCCO",
        help_text=_(
            "Palavras que devem aparecer no campo OBJETO dos dados do "
            "Gescon para identificar se o contrato pertence ao ILB. "
            "<ul><li>Informe uma palavra por linha.</li>"
            "<li>Ocorrendo qualquer uma das palavras, o contrato será "
            "importado.</li></ul>"
        ),
        widget=forms.Textarea(),
    )
    palavras_excluir = forms.CharField(
        required=True,
        label=_("palavras de exclusão"),
        initial="DTCOM",
        help_text=_(
            "Palavras que não podem aparecer no campo OBJETO dos dados do "
            "Gescon."
            "<ul><li>Informe uma palavra por linha.</li>"
            "<li>Ocorrendo qualquer uma das palavras, o contrato será "
            "ignorado.</li></ul>"
        ),
        widget=forms.Textarea(),
    )
    orgaos_gestores = forms.CharField(
        required=True,
        label=_("Órgãos gestores"),
        initial="SCCO",
        help_text=_(
            "Siglas de órgãos gestores que devem aparecer no campo"
            "ORGAOSGESTORESTITULARES"
            "<ul><li>Informe um sigla por linha.</li>"
            "<li>Ocorrendo qualquer uma das siglas, o contrato será "
            "importado.</li></ul>"
        ),
        widget=forms.Textarea(),
    )
