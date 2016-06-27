from itertools import chain

from django.forms.widgets import (CheckboxInput, CheckboxSelectMultiple,
                                  RadioChoiceInput, RadioFieldRenderer,
                                  RadioSelect)
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from sigi.apps.diagnosticos.models import Escolha


class EavCheckboxSelectMultiple(CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            label_for = u' for="%s"' % final_attrs['id']

            # Caso exista uma pergunta para abrir
            # adiciona um atripbuto no checkbox
            schema_to_open = Escolha.objects.get(pk=option_value).schema_to_open
            if schema_to_open:
                final_attrs['schema_to_open'] = schema_to_open.name

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))


class EavRadioFieldRenderer(RadioFieldRenderer):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            final_attrs = self.attrs.copy()

            # Caso exista uma pergunta para abrir
            # adiciona um atripbuto no checkbox
            if choice[0]:
                schema_to_open = Escolha.objects.get(pk=choice[0]).schema_to_open
                if schema_to_open:
                    final_attrs['schema_to_open'] = schema_to_open.name

            yield RadioChoiceInput(self.name, self.value, final_attrs, choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]

        final_attrs = self.attrs.copy()

        # Caso exista uma pergunta para abrir
        # adiciona um atripbuto no checkbox
        schema_to_open = Escolha.objects.get(pk=self.value).schema_to_open
        if schema_to_open:
            final_attrs['schema_to_open'] = schema_to_open.name

        return RadioChoiceInput(self.name, self.value, final_attrs, choice, idx)


class EavRadioSelect(RadioSelect):
    renderer = EavRadioFieldRenderer
