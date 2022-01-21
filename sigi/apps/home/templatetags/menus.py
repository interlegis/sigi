import yaml
from django import template
from django.conf import settings

register = template.Library()

with open(settings.MENU_FILE, 'r') as menu_file:
    menus = yaml.load(menu_file, yaml.FullLoader)

@register.inclusion_tag('menus/menu.html', takes_context=True)
def show_menu(context, menu_id):
    return {'menu_items': menus[menu_id], 'request': context.request}
