# -*- coding: utf-8 -*-


def get_li_clear_all_filters(res):
    text = res.html.find(text="Clear All Filters")
    li = text.find_parent("li")
    assert li
    return li


def test_clear_all_filters_is_disabled_if_no_filter_was_used(app):
    res = app.get("/parlamentares/parlamentar/")
    assert res.status_code == 200
    li = get_li_clear_all_filters(res)
    assert "disabled" in li.attrs["class"]


def test_clear_all_filters_is_enabled_if_some_filter_was_used(app):
    # now we filter by capital letter
    res = app.get("/parlamentares/parlamentar/?nome_completo=B")
    assert res.status_code == 200
    li = get_li_clear_all_filters(res)
    assert "disabled" not in li.attrs["class"]
