from django import forms
from django.utils.translation import gettext as _
from material.admin.widgets import MaterialAdminTextareaWidget
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.eventos.models import Convite, ModeloDeclaracao, Evento
from sigi.apps.parlamentares.models import Parlamentar


class EventoAdminForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = (
            "tipo_evento",
            "nome",
            "descricao",
            "virtual",
            "solicitante",
            "num_processo",
            "data_pedido",
            "data_inicio",
            "data_termino",
            "carga_horaria",
            "casa_anfitria",
            "municipio",
            "observacao",
            "local",
            "publico_alvo",
            "total_participantes",
            "status",
            "data_cancelamento",
            "motivo_cancelamento",
        )

    def clean(self):
        cleaned_data = super(EventoAdminForm, self).clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_termino = cleaned_data.get("data_termino")

        if data_inicio > data_termino:
            raise forms.ValidationError(
                _("Data término deve ser posterior à data inicio"),
                code="invalid_period",
            )


class SelecionaModeloForm(forms.Form):
    modelo = forms.ModelChoiceField(
        queryset=ModeloDeclaracao.objects.all(),
        required=True,
        label=_("Modelo de declaração"),
    )


class ConviteForm(forms.ModelForm):
    class Meta:
        model = Convite
        fields = ["nomes_participantes"]
        widgets = {"nomes_participantes": MaterialAdminTextareaWidget}


class CasaForm(forms.ModelForm):
    class Meta:
        model = Orgao
        fields = ["cnpj", "logradouro", "bairro", "cep", "email", "brasao"]


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            "nome",
            "sexo",
            "cpf",
            "identidade",
            "nota",
            "email",
            "redes_sociais",
        ]
        widgets = {
            "nota": MaterialAdminTextareaWidget,
            "redes_sociais": MaterialAdminTextareaWidget,
        }


class ParlamentarForm(forms.ModelForm):
    class Meta:
        model = Parlamentar
        fields = [
            "nome_completo",
            "nome_parlamentar",
            "data_nascimento",
            "cpf",
            "identidade",
            "telefones",
            "email",
            "redes_sociais",
            "observacoes",
        ]
        widgets = {
            "nome_completo": forms.HiddenInput,
            "redes_sociais": MaterialAdminTextareaWidget,
            "observacoes": MaterialAdminTextareaWidget,
            "status_mandato": forms.RadioSelect,
        }
