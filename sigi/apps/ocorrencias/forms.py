from django.forms import ModelForm, ModelChoiceField, HiddenInput, TextInput
from sigi.apps.ocorrencias.models import Ocorrencia, Comentario, Anexo
from sigi.apps.servidores.models import Servico
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.forms.utils import flatatt
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

class AjaxSelect(TextInput):
    url = ""
    def __init__(self, url, attrs=None):
        super(AjaxSelect, self).__init__(attrs)
        self.url = url

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type)
        code_attrs = self.build_attrs(type='hidden', name=name,
                                      id='hidden_'+name)
        if value != '':
            final_attrs['value'] = force_text(self._format_value(value))
        result = format_html('<input{0} />', flatatt(final_attrs)) + "\n"
        result = result + format_html('<input{0} />', flatatt(code_attrs))
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
                  </script>""" % {'name': name, 'url': self.url}
        result = result + mark_safe(js)
        return result

class AnexoForm(ModelForm):
    class Meta:
        model = Anexo
        fields = ['ocorrencia', 'descricao', 'arquivo',]
        widgets = {'ocorrencia': HiddenInput()}

class ComentarioForm(ModelForm):
    encaminhar_setor = ModelChoiceField(
        queryset=Servico.objects.all(),
        cache_choices=True
    )

    class Meta:
        model = Comentario
        fields = ['ocorrencia', 'descricao', 'novo_status', 'encaminhar_setor']
        widgets = {'ocorrencia': HiddenInput(),}

class OcorrenciaForm(ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['casa_legislativa', 'categoria', 'tipo_contato', 'assunto',
                  'prioridade', 'ticket', 'descricao', 'setor_responsavel',]
        widgets = {
            'casa_legislativa': AjaxSelect(
                url=reverse_lazy('painel-buscacasa'),
                attrs={'size':100}
            ),
        }