from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from localflavor.br.forms import BRZipCodeField
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils import valida_cnpj


class AtualizaCasaForm(forms.Form):
    arquivo = forms.FileField(
        required=True,
        label=_("arquivo a importar"),
        help_text=_("Envie um arquivo no formato CSV"),
    )


class OrgaoForm(forms.ModelForm):
    cep = BRZipCodeField(
        label=_("CEP"), help_text=_("Formato") + ": <em>XXXXX-XXX</em>."
    )

    class Meta:
        model = Orgao
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get("nome")
        tipo = cleaned_data.get("tipo")
        municipio = cleaned_data.get("municipio")
        if tipo.sigla == "CM":
            nome_correto = [f"Câmara Municipal de {municipio.nome}"]
        elif tipo.sigla == "AL":
            nome_correto = [
                f"Assembleia Legislativa {conj} {municipio.uf.nome}"
                for conj in ["da", "de", "do"]
            ]
        else:
            nome_correto = [nome]
        if nome not in nome_correto:
            self.add_error(
                "nome",
                ValidationError(
                    _(
                        "O nome '%(nome)s' não é adequado para uma %(tipo)s. "
                        "O correto deve ser '%(nome_correto)s'."
                    ),
                    code="invalid_nome",
                    params={
                        "nome": nome,
                        "tipo": tipo.nome,
                        "nome_correto": nome_correto[0],
                    },
                ),
            )
        return cleaned_data

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj")
        if cnpj != "" and not valida_cnpj(cnpj):
            raise ValidationError(
                _("CNPJ inválido. Dígito verificador não confere."),
                code="invalid_cnpj",
            )
        return cnpj


class PortfolioForm(forms.Form):
    ACAO_CHOICES = (("ADD", _("Adicionar")), ("DEL", _("Remover")))
    acao = forms.ChoiceField(
        label=_("Ação"),
        choices=ACAO_CHOICES,
        initial="ADD",
        widget=forms.RadioSelect,
    )
    gerente = forms.ModelChoiceField(
        queryset=Servidor.objects.all(), label=_("Atribuir para")
    )

    # O label precisa ser trocado dependendo da região que se está visualizando
    def __init__(self, label=_("Atribuir para"), *args, **kwargs):
        super(PortfolioForm, self).__init__(*args, **kwargs)
        self.fields["gerente"].label = label


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            "nome",
            "cpf",
            "identidade",
            "sexo",
            "data_nascimento",
            "setor",
            "cargo",
            "funcao",
            "tempo_de_servico",
            "nota",
            "email",
            "redes_sociais",
        ]


class CnpjErradoForm(forms.Form):
    has_convenio = forms.BooleanField(
        label=_("Mostrar apenas órgãos com convênio"),
        required=False,
        initial=False,
    )
