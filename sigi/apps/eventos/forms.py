from django import forms
from django.utils.translation import gettext as _
from sigi.apps.eventos.models import ModeloDeclaracao, Evento

class EventoAdminForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ('tipo_evento', 'nome', 'descricao', 'virtual', 'solicitante',
                  'num_processo', 'data_pedido', 'data_inicio', 'data_termino',
                  'carga_horaria', 'casa_anfitria', 'municipio', 'observacao',
                  'local', 'publico_alvo', 'total_participantes', 'status',
                  'data_cancelamento', 'motivo_cancelamento', )

    def clean(self):
        cleaned_data = super(EventoAdminForm, self).clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_termino = cleaned_data.get("data_termino")

        if data_inicio > data_termino:
            raise forms.ValidationError(
                _("Data término deve ser posterior à data inicio"),
                code="invalid_period"
            )

class SelecionaModeloForm(forms.Form):
    modelo = forms.ModelChoiceField(
        queryset=ModeloDeclaracao.objects.all(),
        required=True,
        label=_("Modelo de declaração"),
    )