from django import forms
from django.utils.translation import gettext as _
from localflavor.br.forms import BRZipCodeField
from material.admin.widgets import MaterialAdminTextareaWidget
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.servidores.models import Servidor


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
        widgets = {
            "redes_sociais": MaterialAdminTextareaWidget,
        }
