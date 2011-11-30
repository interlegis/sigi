# -*- coding: utf8 -*-

from copy import deepcopy
from django import forms
from django.forms.forms import BoundField
from sigi.apps.casas.models import CasaLegislativa, Funcionario
from sigi.apps.diagnosticos.models import Diagnostico
from eav.forms import BaseDynamicEntityForm

class DiagnosticoForm(BaseDynamicEntityForm):
    """Classe responsável por contruir o formulário,
    vinculando ao modelo Diagnostico
    """
    model = Diagnostico


class DiagnosticoMobileForm(BaseDynamicEntityForm):
    """Classe responsável por construir o formulário
    para ser usado no ambiente mobile, a partir do
    do modelo Diagnostico, como também organizar sua
    estrutura via categorias.
    """
    class Meta:
        model = Diagnostico

    def __init__(self, data=None, category=None, *args, **kwargs):
        super(BaseDynamicEntityForm, self).__init__(data, *args, **kwargs)
        self._build_dynamics_fields(category)

    def __iter__(self):
        # ordena os campos do formulario usando o atributo label
        fields_by_label = [(field.label, name, field) for name, field in self.fields.items()]
        for label, name, field in sorted(fields_by_label):
            yield BoundField(self, field, name)

    def _build_dynamics_fields(self, category):
        """Método da classe ``BaseDynamicEntityForm`` sobrescrita,
        para que as perguntas sejam agrupadas dentro das suas
        categorias.
            * category = ID da Categoria
        """
        # Caso seja as duas primeiras categorias, utilize
        # os campos do modelo
        if int(category) in (0, 1, ):
            self.fields = deepcopy(self.base_fields)
        else:
            self.fields = dict()

        # Se determinada pergunta é da categoria pesquisada,
        # então, gere o campo no formulário.
        for schema in self.instance.get_schemata():

            if not schema.categoria_id == int(category):
                continue

            defaults = {
                'label':     schema.title.capitalize(),
                'required':  schema.required,
                'help_text': schema.help_text,
            }

            datatype = schema.datatype
            if datatype == schema.TYPE_MANY:
                choices = getattr(self.instance, schema.name)
                defaults.update({'queryset': schema.get_choices(),
                                 'initial': [x.pk for x in choices]})
            elif datatype == schema.TYPE_ONE:
                choice = getattr(self.instance, schema.name)
                defaults.update({'queryset': schema.get_choices(),
                                 'initial': choice.pk if choice else None,
                                 # if schema is required remove --------- from ui
                                 'empty_label' : None if schema.required else u"---------"})

            extra = self.FIELD_EXTRA.get(datatype, {})
            if hasattr(extra, '__call__'):
                extra = extra(schema)
            defaults.update(extra)

            MappedField = self.FIELD_CLASSES[datatype]
            self.fields[schema.name] = MappedField(**defaults)

            # fill initial data (if attribute was already defined)
            value = getattr(self.instance, schema.name)
            if value and not datatype in (schema.TYPE_ONE, schema.TYPE_MANY):    # choices are already done above
                self.initial[schema.name] = value

class CasaLegislativaMobileForm(forms.ModelForm):
    pass
    class Meta:
        model = CasaLegislativa
        fields = ('cnpj', 'logradouro', 'bairro', 'cep', 'email', 'pagina_web')

class FuncionariosMobileForm(forms.ModelForm):
    pass
    class Meta:
        model = Funcionario
        fields = ('nome', 'email', 'cargo', 'funcao', 'tempo_de_servico')
