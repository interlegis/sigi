# -*- coding: utf-8 -*-
import pytest
from django_webtest import DjangoTestApp, WebTestMixin


@pytest.fixture(scope='function')
def app(request):
    """WebTest's TestApp.

    Patch and unpatch settings before and after each test.

    WebTestMixin, when used in a unittest.TestCase, automatically calls
    _patch_settings() and _unpatchsettings.

    source: https://gist.github.com/magopian/6673250
    """
    wtm = WebTestMixin()
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return DjangoTestApp()
