#
# Default Django settings for SIGI.
#
#   (!!!)
#
#   DON'T CHANGE THIS FILE, USE local_settings.py. YOU GET A TEMPLATE IN
#   local_settings.template (COPY HIM TO local_settings.py AND MAKE YOUR
#   NECESSARY CHANGES.
#

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '../..')
PROJECT_DIR = BASE_DIR + '/sigi'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# I can't determine this, use local_settings.py.
ADMINS = (('root', 'root@localhost'),)
MANAGERS = ADMINS
SERVER_EMAIL = 'root@localhost'
DEFAULT_FROM_EMAIL = 'noreply@localhost'

INTERNAL_IPS = ('127.0.0.1',)

DATABASE_ENGINE = 'postgresql_psycopg2'
#DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'sigi3'
DATABASE_USER = 'administrador'
DATABASE_PASSWORD = 'interlegis' 
DATABASE_HOST = '10.1.10.102'
DATABASE_PORT = '5432'          

TIME_ZONE = 'Brazil/East'
LANGUAGE_CODE = 'pt-br'
SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

CACHE_BACKEND = 'dummy:///'
CACHE_MIDDLEWARE_SECONDS = 60
CACHE_MIDDLEWARE_KEY_PREFIX = 'sigi'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = False

# Used to provide a seed in secret-key hashing algorithms. Set this to
# a random string in your local_settings.py - the longer, the better.
SECRET_KEY = 'set-this-in-your-local_settings.py!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'sigi.context_processors.charts_data',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'sigi.urls'

TEMPLATE_DIRS = (
    PROJECT_DIR + '/templates',
)

FIXTURE_DIRS = (PROJECT_DIR + '/fixtures',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',      # http://django-command-extensions.googlecode.com
    'googlecharts',           # http://github.com/jacobian/django-googlecharts
    'treemenus',              # http://django-treemenus.googlecode.com
    'reporting',              # http://github.com/marinho/geraldo
    'sigi.apps.casas',
    'sigi.apps.contatos',
    'sigi.apps.convenios',
    'sigi.apps.inventario',
    'sigi.apps.mesas',
    'sigi.apps.parlamentares',
    'sigi.apps.servicos',
    'sigi.apps.relatorios',
)

try:
    from local_settings import *
except ImportError:
    from warnings import warn
    msg = "You don't have local_settings.py file, using defaults settings."
    try:
        # don't work in Python 2.4 or before
        warn(msg, category=ImportWarning)
    except NameError:
        warn(msg)
