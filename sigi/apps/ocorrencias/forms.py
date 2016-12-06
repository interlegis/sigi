# -*- coding: utf-8 -*-
#
# sigi.apps.ocorrencias.forms
#
# Copyright (c) 2015 by Interlegis
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
from django.core.urlresolvers import reverse_lazy
from django.forms import HiddenInput, ModelChoiceField, ModelForm, TextInput
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from sigi.apps.ocorrencias.models import Anexo, Comentario, Ocorrencia
from sigi.apps.servidores.models import Servico


class AjaxSelect(TextInput):
    url = ""
    def __init__(self, url, attrs=None):
        super(AjaxSelect, self).__init__(attrs)
        self.url = url
        
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type)
        code_attrs = self.build_attrs(type='hidden', name=name, id='hidden_'+name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
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
    encaminhar_setor = ModelChoiceField(queryset=Servico.objects.all())
        
    class Meta:
        model = Comentario
        fields = ['ocorrencia', 'descricao', 'novo_status', 'encaminhar_setor']
        widgets = {'ocorrencia': HiddenInput(),}

class OcorrenciaForm(ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['casa_legislativa', 'categoria', 'tipo_contato', 'assunto', 'prioridade', 'ticket',
                  'descricao', 'setor_responsavel',]
        widgets = {'casa_legislativa': AjaxSelect(url=reverse_lazy('painel-buscacasa'), attrs={'size':100}), }
