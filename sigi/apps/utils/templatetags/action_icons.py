from django import template

register = template.Library()

ACTION_LIST = {
    "delete_selected": "delete_forever",
    "add_to_cart": "add_shopping_cart",
    "remove_from_cart": "remove_shopping_cart",
    "calcular_data_uso": "functions",
}


@register.simple_tag
def action_icon(action_name):
    if action_name in ACTION_LIST:
        return ACTION_LIST[action_name]
    else:
        return "play_arrow"
