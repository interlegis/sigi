from os.path import dirname

import yaml
from django import template

register = template.Library()

menus = yaml.load(open(dirname(__file__) + '/menu_conf.yaml', 'r'))


@register.inclusion_tag('menus/menu.html', takes_context=True)
def show_menu(context, menu_id):
    base_url = context['request'].build_absolute_uri('/')
    menus = yaml.load(open(dirname(__file__) + '/menu_conf.yaml', 'r'))
    return dict(menu_items=menus[menu_id], base_url=base_url)


@register.inclusion_tag('menus/menu_item.html')
def show_menu_item(menu_item, base_url):
    return dict(menu_item=menu_item, base_url=base_url)
