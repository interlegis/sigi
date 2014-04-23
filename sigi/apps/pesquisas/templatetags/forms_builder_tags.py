from django import template
from forms_builder.forms.templatetags.forms_builder_tags import BuiltFormNode
from sigi.apps.pesquisas.models import Pesquisa
from sigi.apps.pesquisas.forms import PesquisaForm

register = template.Library()

class BuiltPesquisaNode(BuiltFormNode):
    form_class = Pesquisa
    form_for_form_class = PesquisaForm

@register.tag
def render_built_form(parser, token):
    """
    render_build_form takes one argument in one of the following formats:

    {% render_build_form form_instance %}
    {% render_build_form form=form_instance %}
    {% render_build_form id=form_instance.id %}
    {% render_build_form slug=form_instance.slug %}

    """
    try:
        _, arg = token.split_contents()
        if "=" not in arg:
            arg = "form=" + arg
        name, value = arg.split("=", 1)
        if name not in ("form", "id", "slug"):
            raise ValueError
    except ValueError:
        e = ()
        raise template.TemplateSyntaxError(render_built_form.__doc__)
    return BuiltPesquisaNode(name, value)
