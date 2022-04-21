from django import template

register = template.Library()


@register.inclusion_tag("pagination/paginator.html")
def smart_paginator(page_obj, querystring=None):
    if querystring:
        querystring = "?" + querystring + "&"
    else:
        querystring = "?"

    page_range = page_obj.paginator.page_range
    mid = len(page_range) // 2

    range = list(
        set(page_range[:3])
        | set(page_range[mid - 2 : mid + 1])
        | set(page_range[-3:])
        | set(page_range[page_obj.number - 2 : page_obj.number + 1])
    )
    range.sort()

    last = range[0] - 1
    page_range = []

    for p in range:
        if p - 1 != last:
            if p - 2 == last:
                page_range.append(p - 1)
            else:
                page_range.append(None)
        page_range.append(p)
        last = p

    return dict(
        page_obj=page_obj, querystring=querystring, page_range=page_range
    )


@register.inclusion_tag("menus/menu_item.html")
def show_menu_item(menu_item, base_url):
    return dict(menu_item=menu_item, base_url=base_url)
