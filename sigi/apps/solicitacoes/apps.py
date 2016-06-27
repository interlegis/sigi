# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django import apps
from django.utils.translation import ugettext_lazy as _


class AppConfig(apps.AppConfig):
    name = u'solicitacoes'
    verbose_name = _(u'Solicitações')
