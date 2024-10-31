from django import forms
from django.utils.translation import gettext as _
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.espacos.models import Espaco, Reserva
from sigi.apps.eventos.models import (
    Convite,
    ModeloDeclaracao,
    Evento,
    TipoEvento,
    Solicitacao,
)
from sigi.apps.parlamentares.models import Parlamentar


class EventoAdminForm(forms.ModelForm):
    espaco = forms.ModelChoiceField(
        label=_("Reservar espaço"),
        required=False,
        queryset=Espaco.objects.filter(reserva_eventos=True),
    )

    class Meta:
        model = Evento
        fields = (
            "tipo_evento",
            "nome",
            "turma",
            "descricao",
            "virtual",
            "solicitante",
            "num_processo",
            "data_pedido",
            "data_recebido_coperi",
            "data_inicio",
            "data_termino",
            "hora_inicio",
            "hora_termino",
            "carga_horaria",
            "casa_anfitria",
            "espaco",
            "observacao",
            "local",
            "publico_alvo",
            "total_participantes",
            "status",
            "publicar",
            "moodle_courseid",
            "chave_inscricao",
            "perfil_aluno",
            "observacao_inscricao",
            "contato_inscricao",
            "telefone_inscricao",
            "contato",
            "telefone",
            "banner",
            "data_cancelamento",
            "motivo_cancelamento",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.reserva:
            self.initial["espaco"] = self.instance.reserva.espaco

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_termino = cleaned_data.get("data_termino")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_termino = cleaned_data.get("hora_termino")
        publicar = cleaned_data.get("publicar")

        if data_inicio and data_termino and data_inicio > data_termino:
            raise forms.ValidationError(
                _("Data término deve ser posterior à data inicio"),
                code="invalid_period",
            )

        if hora_inicio and hora_termino and hora_inicio > hora_termino:
            raise forms.ValidationError(
                _("Hora término deve ser posterior à hora inicio"),
                code="invalid_period",
            )

        if publicar and (data_inicio is None or data_termino is None):
            raise forms.ValidationError(
                _(
                    "Para publicar no site é preciso ter data início e "
                    "data término"
                ),
                code="cannot_publish",
            )

        espaco = cleaned_data["espaco"]
        if (self.instance.reserva is None) and (espaco is None):
            return
        if self.instance.reserva is None:
            self.instance.reserva = Reserva(espaco=espaco)
        elif espaco is None:
            self.instance.reserva = None
        else:
            self.instance.reserva.espaco = espaco

        if self.instance.reserva:
            self.instance.update_reserva()

        return cleaned_data


class SelecionaModeloForm(forms.Form):
    modelo = forms.ModelChoiceField(
        queryset=ModeloDeclaracao.objects.all(),
        required=True,
        label=_("Modelo de declaração"),
    )


class EventosPorUfForm(forms.Form):
    MODO_CHOICES = (
        ("V", _("Virtual")),
        ("P", _("Presencial")),
    )
    data_inicio = forms.DateField(required=True, label=_("data de início"))
    data_fim = forms.DateField(required=True, label=_("data de término"))
    categoria = forms.MultipleChoiceField(
        required=False,
        label=_("Categoria"),
        choices=TipoEvento.CATEGORIA_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    virtual = forms.MultipleChoiceField(
        required=False,
        label=_("Modo"),
        choices=MODO_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Media:
        css = {"all": ["css/change_form.css"]}
        js = [
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/change_form.js",
            "admin/js/vendor/select2/i18n/pt-BR.js",
            "material/admin/js/widgets/TimeInput.js",
            "admin/js/core.js",
            "/admin/jsi18n/",
        ]


class SolicitacoesPorPeriodoForm(forms.Form):
    MODO_CHOICES = (
        (True, _("Virtual")),
        (False, _("Presencial")),
    )
    data_inicio = forms.DateField(required=True, label=_("data de início"))
    data_fim = forms.DateField(required=True, label=_("data de término"))
    tipos_evento = forms.ModelMultipleChoiceField(
        required=False,
        label=_("Tipos de evento"),
        queryset=TipoEvento.objects.all(),
    )
    virtual = forms.MultipleChoiceField(
        required=False,
        label=_("Modo"),
        choices=MODO_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    status = forms.MultipleChoiceField(
        required=False,
        label=_("Status"),
        choices=Solicitacao.STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Media:
        css = {"all": ["css/change_form.css"]}
        js = [
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/change_form.js",
            "admin/js/vendor/select2/i18n/pt-BR.js",
            "material/admin/js/widgets/TimeInput.js",
            "admin/js/core.js",
            "/admin/jsi18n/",
        ]


class ConviteForm(forms.ModelForm):
    class Meta:
        model = Convite
        fields = ["nomes_participantes"]


class CasaForm(forms.ModelForm):
    class Meta:
        model = Orgao
        fields = [
            "cnpj",
            "logradouro",
            "bairro",
            "cep",
            "telefone_geral",
            "email",
            "brasao",
        ]


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
            "status_mandato": forms.RadioSelect,
        }
