#!/usr/bin/env python
# -*- mode: python -*-
import os, sys

sys.path.insert(0, '/var/aplicacoes/django/sigi')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigi.settings'

from django.core.management.validation import get_validation_errors
try:
        from cStringIO import StringIO
except ImportError:
        from StringIO import StringIO
s = StringIO()
num_errors = get_validation_errors(s, None) 

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
