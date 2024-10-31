from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.core.validators import FileExtensionValidator
from django.forms.utils import flatatt
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ngettext, gettext as _
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.eventos.models import TipoEvento
from sigi.apps.ocorrencias.models import Ocorrencia, Comentario, Anexo
from sigi.apps.servidores.models import Servico
from sigi.apps.parlamentares.models import Parlamentar, Senador


class AjaxSelect(forms.TextInput):
    url = ""

    def __init__(self, url, attrs=None):
        super(AjaxSelect, self).__init__(attrs)
        self.url = url

    def render(self, name, value, attrs=None):
        if value is None:
            value = ""
        final_attrs = self.build_attrs(attrs, type=self.input_type)
        code_attrs = self.build_attrs(
            type="hidden", name=name, id="hidden_" + name
        )
        if value != "":
            final_attrs["value"] = force_str(self._format_value(value))
        result = format_html("<input{0} />", flatatt(final_attrs)) + "\n"
        result = result + format_html("<input{0} />", flatatt(code_attrs))
        js = """
                  <script type="text/javascript">
                      $( document ).ready(function() {
                        $("#id_%(name)s").autocomplete({
                            source: "%(url)s",
                            select: function(event, ui) {
                                $("#hidden_%(name)s").attr("value", ui.item.value);
                                ui.item.value = ui.item.label
                            }
                        })
                      });
                  </script>""" % {
            "name": name,
            "url": self.url,
        }
        result = result + mark_safe(js)
        return result


class AnexoForm(forms.ModelForm):
    class Meta:
        model = Anexo
        fields = [
            "descricao",
            "arquivo",
        ]


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = [
            "ocorrencia",
            "descricao",
            "novo_status",
        ]
        widgets = {"ocorrencia": forms.HiddenInput}


class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = [
            "casa_legislativa",
            "categoria",
            "tipo_contato",
            "assunto",
            "prioridade",
            "ticket",
            "descricao",
        ]
        # widgets = {
        #     "casa_legislativa": AutocompleteSelect(
        #         Ocorrencia.casa_legislativa.field, admin.site
        #     )
        # }


class OcorrenciaChangeForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ["prioridade", "processo_sigad"]


class AutorizaOficinaForm(forms.ModelForm):
    oficinas = forms.ModelMultipleChoiceField(
        label=_("Oficinas"),
        queryset=TipoEvento.objects.filter(casa_solicita=True),
        required=True,
        help_text=_("Selecione as oficinas que deseja autorizar."),
        widget=forms.CheckboxSelectMultiple,
    )
    virtual = forms.BooleanField(label=_("Virtual"))
    data_inicio = forms.DateField(label=_("Data de início"), required=True)
    data_termino = forms.DateField(label=_("Data de término"), required=True)

    class Meta:
        model = Ocorrencia
        fields = ["oficinas", "virtual", "data_inicio", "data_termino"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        autorizadas = self.instance.evento_set.values_list(
            "tipo_evento_id", flat=True
        )
        self.fields["oficinas"].queryset = TipoEvento.objects.filter(
            id__in=self.instance.infos["solicita_oficinas"]["oficinas"]
        ).exclude(id__in=autorizadas)


class CasaForm(forms.ModelForm):
    class Meta:
        model = Orgao
        fields = [
            "cnpj",
            "data_instalacao",
            "horario_funcionamento",
            "logradouro",
            "bairro",
            "cep",
            "telefone_geral",
            "email",
            "pagina_web",
            "foto",
            "brasao",
        ]


class PresidenteForm(forms.ModelForm):
    parlamentar = forms.ModelChoiceField(queryset=Parlamentar.objects.none())

    class Meta:
        model = Parlamentar
        fields = [
            "parlamentar",
            "data_nascimento",
            "cpf",
            "identidade",
            "telefones",
            "email",
            "redes_sociais",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parlamentar"].queryset = (
            self.instance.casa_legislativa.parlamentar_set.all()
        )


class ContatoForm(forms.ModelForm):
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


class DocumentoForm(forms.ModelForm):
    arquivo = forms.FileField(
        label=_("Solicitação assinada"),
        help_text=_("Utilize o formato PDF apenas"),
        validators=[
            FileExtensionValidator(
                ["pdf"], _("Somente arquivos em formato PDF"), "pdf_only"
            )
        ],
    )

    class Meta:
        model = Anexo
        fields = ["arquivo"]


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["descricao"]


class ComentarioInternoForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["descricao", "interno", "novo_status"]


class SolicitaTreinamentoForm(forms.ModelForm):
    MODALIDADE_CHOICES = (
        ("R", _("Remota")),
        ("P", _("Presencial")),
    )
    numero_oficio = forms.CharField(
        max_length=50,
        label=_("número do ofício"),
        required=True,
        help_text=_(
            "Informe um número de ofício válido do protocoloco da sua "
            "Casa Legislativa para ser impresso no ofício de solicitação."
        ),
    )
    modalidade = forms.ChoiceField(
        label=_("modalidade"),
        choices=MODALIDADE_CHOICES,
        initial="R",
        required=True,
        widget=forms.RadioSelect,
    )
    oficinas = forms.ModelMultipleChoiceField(
        label=_("Oficinas"),
        queryset=TipoEvento.objects.filter(casa_solicita=True),
        required=True,
        help_text=_("Selecione as oficinas que deseja participar."),
        widget=forms.CheckboxSelectMultiple,
    )

    senadores = forms.ModelMultipleChoiceField(
        label=_("Senadores"),
        queryset=Senador.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text=_(
            "O ofício de solicitação precisa passar pelo gabinete de "
            "pelo menos um Senador, para que as oficinas sejam "
            "autorizadas. Indique os Senadores para os quais deseja "
            "enviar o ofício de solicitação, ou deixe todos marcados "
            "para que o ofício seja encaminhado a todos os Senadores "
            "do seu Estado."
        ),
    )

    class Meta:
        model = Ocorrencia
        fields = ["numero_oficio", "modalidade", "oficinas", "senadores"]

    def __init__(self, *args, **kwargs):
        senadores = kwargs.pop("senadores")
        super().__init__(*args, **kwargs)
        self.fields["senadores"].queryset = senadores
