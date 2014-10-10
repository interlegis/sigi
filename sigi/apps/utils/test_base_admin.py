# -*- coding: utf-8 -*-


def test_clear_all_filters_is_disabled_if_no_filter_was_used(admin_client):
    response = admin_client.get('/parlamentares/parlamentar', follow=True)
    assert response.status_code == 200
    assert '<li class="clear-all-filter disabled"><a href="?">Clear All Filters</a></li>' in response.content


def test_clear_all_filters_is_enabled_if_some_filter_was_used(admin_client):
    # now we filter by capital letter
    response = admin_client.get('/parlamentares/parlamentar/?nome_completo=B', follow=True)
    assert response.status_code == 200
    # and there is no "disabled" css class
    assert '<li class="clear-all-filter"><a href="?">Clear All Filters</a></li>' in response.content
