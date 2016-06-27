# -*- coding: utf-8 -*-
import pytest
from django_webtest import DjangoTestApp, WebTestMixin

DEFAULT_MARK = object()


class SigiTestApp(DjangoTestApp):

    def __init__(self, extra_environ=None, relative_to=None, default_user=None):
        super(SigiTestApp, self).__init__(extra_environ, relative_to)
        self.default_user = default_user

    def get(self, url, params=None, headers=None, extra_environ=None,
            status=None, expect_errors=False, user=DEFAULT_MARK, auto_follow=True,
            content_type=None, **kwargs):
            # note we altered the default values for user and auto_follow

        if user is DEFAULT_MARK:  # a trick to allow explicit user=None
            user = self.default_user

        return super(SigiTestApp, self).get(url, params, headers, extra_environ,
                                            status, expect_errors, user, auto_follow,
                                            content_type, **kwargs)


@pytest.fixture(scope='function')
def app(request, admin_user):
    """WebTest's TestApp.

    Patch and unpatch settings before and after each test.

    WebTestMixin, when used in a unittest.TestCase, automatically calls
    _patch_settings() and _unpatchsettings.

    source: https://gist.github.com/magopian/6673250
    """
    wtm = WebTestMixin()
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return SigiTestApp(default_user=admin_user.username)
