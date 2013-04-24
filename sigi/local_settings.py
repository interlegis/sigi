# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '../..')
PROJECT_DIR = BASE_DIR + '/sigi'

# Postgres local server needed
#DATABASE_ENGINE = 'postgresql_psycopg2'
#DATABASE_NAME = 'sigi'
#DATABASE_USER = 'sigi'
#DATABASE_PASSWORD = '123456'
#DATABASE_HOST = 'localhost'
#DATABASE_PORT = '5432'

# SQLite local setting
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASE_NAME = BASE_DIR + '/sigi.db'

ADMINS = (('sigi', 'sigi@interlegis.leg.br'),)
MANAGERS = ADMINS
SERVER_EMAIL = 'sigi@interlegis.leg.br'
DEFAULT_FROM_EMAIL = 'sigi@interlegis.leg.br'
EMAIL_SUBJECT_PREFIX = u'[SIGI]'

# Keep ModelBackend around for per-user permissions and maybe a local superuser.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
