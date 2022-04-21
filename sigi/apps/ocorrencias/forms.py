from django import forms
from sigi.apps.ocorrencias.models import Ocorrencia, Comentario, Anexo
from sigi.apps.servidores.models import Servico
from django.utils.encoding import force_str
from django.utils.html import format_html
from django.forms.utils import flatatt
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from material.admin.widgets import MaterialAdminTextareaWidget
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib import admin


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
            "ocorrencia",
            "descricao",
            "arquivo",
        ]
        widgets = {"ocorrencia": forms.HiddenInput()}


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = [
            "ocorrencia",
            "descricao",
            "novo_status",
        ]
        widgets = {
            "ocorrencia": forms.HiddenInput(),
            "descricao": MaterialAdminTextareaWidget(),
        }


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
        widgets = {
            "casa_legislativa": AutocompleteSelect(
                Ocorrencia.casa_legislativa.field, admin.site
            )
        }
        # widgets = {
        #     'casa_legislativa': AjaxSelect(
        #         url=reverse_lazy('painel-buscacasa'),
        #         attrs={'size':100}
        #     ),
        # }
