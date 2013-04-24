# coding= utf-8
#
# Default Django settings for SIGI.
#
#   (!!!)
#
#   DON'T CHANGE THIS FILE, USE local_settings.py. YOU GET A TEMPLATE IN
#   local_settings.template (COPY HIM TO local_settings.py AND MAKE YOUR
#   NECESSARY CHANGES.
#
import logging
from local_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1',)

TIME_ZONE = 'Brazil/East'
LANGUAGE_CODE = 'pt-br'
DEFAULT_CHARSET = 'utf-8'
SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/sigi/media/'
ADMIN_MEDIA_PREFIX = '/sigi/admin_media/'

CACHE_BACKEND = 'locmem://' # Considerar seriamente a possibilidade de usar o memcached
CACHE_MIDDLEWARE_SECONDS = 60
CACHE_MIDDLEWARE_KEY_PREFIX = 'sigi'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = False

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
    'django.core.context_processors.request',
    'sigi.context_processors.charts_data',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
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
    'sigi.apps.servidores',
    'sigi.apps.diagnosticos',
    'sigi.apps.ocorrencias',
    'sigi.apps.servicos',
    'sigi.apps.relatorios',
    'sigi.apps.metas',
    'sigi.apps.financeiro',
)

#try:
#    from local_settings import *
#except ImportError:
#    from warnings import warn
#    msg = "You don't have local_settings.py file, using defaults settings."
#    try:
#        # don't work in Python 2.4 or before
#        warn(msg, category=ImportWarning)
#    except NameError:
#        warn(msg)
