#!/usr/bin/env python
# -*- mode: python -*-
import os, sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '../..'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'sigi.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
