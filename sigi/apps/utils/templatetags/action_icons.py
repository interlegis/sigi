from django import template

register = template.Library()

ACTION_LIST = {
    "delete_selected": "delete_forever",
    "add_to_cart": "add_shopping_cart",
    "remove_from_cart": "remove_shopping_cart",
    "calcular_data_uso": "functions",
}

ACTION_PREFIXES = {
    "cancelar": "cancel",
    "ativar": "check_circle",
}


@register.simple_tag
def action_icon(action_name):
    if action_name in ACTION_LIST:
        return ACTION_LIST[action_name]
    else:
        for prefix in ACTION_PREFIXES:
            if prefix in action_name:
                return ACTION_PREFIXES[prefix]
    return "play_arrow"
