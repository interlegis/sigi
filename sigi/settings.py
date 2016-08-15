# -*- coding: utf-8 -*-
"""
Django settings for sigi project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from os.path import dirname

import django.conf.global_settings as DEFAULT_SETTINGS
import ldap
from decouple import Csv, config
from dj_database_url import parse as db_url
from django_auth_ldap.config import GroupOfNamesType, LDAPSearch
from easy_thumbnails.conf import Settings as thumbnail_settings

PROJECT_DIR = dirname(__file__)
BASE_DIR = dirname(PROJECT_DIR)


def split(linha):
    return [s.strip() for s in linha.split()]

SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=split)

ADMINS = config('ADMINS',
                cast=lambda x: tuple(
                    tuple(user_email.split(':')) for user_email in split(x)),
                default='')
MANAGERS = ADMINS

DATABASES = {
    'default': config('DATABASE_URL', cast=db_url),
    'moodle': config('MOODLE_URL', cast=db_url,
                     default='sqlite:///' +
                     os.path.join(BASE_DIR, 'moodle.db')),
}

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',)
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',)

DATABASE_ROUTERS = ['moodlerouter.MoodleRouter', ]

INSTALLED_APPS = (

    'bootstrap3',
    'django_admin_bootstrapped',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'sigi.apps.home',
    'sigi.apps.contatos',
    'sigi.apps.servidores',
    'sigi.apps.parlamentares',
    'sigi.apps.casas',
    'sigi.apps.convenios',
    'sigi.apps.inventario',
    'sigi.apps.servicos',
    'sigi.apps.metas',
    'sigi.apps.ocorrencias',
    'sigi.apps.financeiro',
    'sigi.apps.diagnosticos',
    'sigi.apps.eventos',

    # Integração com Saberes (moodle)
    'sigi.apps.mdl',
    'sigi.apps.saberes',

    # Third-party apps
    'localflavor',
    'reporting',
    'django_extensions',
    'easy_thumbnails',
    'image_cropping',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sigi.urls'
WSGI_APPLICATION = 'sigi.wsgi.application'

# Internationalization
LANGUAGE_CODE = 'pt-br'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True

gettext_noop = lambda s: s  # for gettext discovery

LANGUAGES = (
    ('en', gettext_noop('English')),
    ('pt-br', gettext_noop('Brazilian Portuguese')),
)

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'sigiStatic'),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# Using pytest directly (without a test runner)
TEST_RUNNER = None

THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS
THUMBNAIL_ALIASES = {
    '': {
        'small': {'size': (300, 225), 'crop': True, },
        'thumb': {'size': (160, 120), 'crop': True, },
        'portrait': {'size': (73, 100), 'crop': True},
        'icon': {'size': (36, 50), 'crop': True},
    },
}
IMAGE_CROPPING_SIZE_WARNING = True
IMAGE_CROPPING_THUMB_SIZE = (800, 600)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'filters': ['require_debug_false'],
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/sigi/application.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

SABERES_REST_PATH = 'webservice/rest/server.php'
OSTICKET_URL = 'https://suporte.interlegis.leg.br/scp/tickets.php?a=search&query=%s'

DEBUG = config('DEBUG', cast=bool, default=False)
TEMPLATE_DEBUG = DEBUG

if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {'SHOW_TEMPLATE_CONTEXT': True, }
    INSTALLED_APPS += ('debug_toolbar',)

    def show_toolbar(request):
        return True
    SHOW_TOOLBAR_CALLBACK = show_toolbar

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }


EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

SERVER_EMAIL = 'sigi-noreply@interlegis.leg.br'
DEFAULT_FROM_EMAIL = 'sigi@interlegis.leg.br'
EMAIL_SUBJECT_PREFIX = '[SIGI]'

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

#### LDAP ###################################################################

AUTH_LDAP_SERVER_URI = config('AUTH_LDAP_SERVER_URI', default='')
usando_ldap = bool(AUTH_LDAP_SERVER_URI)

if usando_ldap:
    AUTH_LDAP_BIND_DN = config('AUTH_LDAP_BIND_DN').decode('utf-8')
    AUTH_LDAP_BIND_PASSWORD = config('AUTH_LDAP_BIND_PASSWORD').decode('utf-8')
    AUTH_LDAP_USER = config('AUTH_LDAP_USER').decode('utf-8')
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        AUTH_LDAP_USER, ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")

    # Set up the basic group parameters.
    AUTH_LDAP_GROUP = config('AUTH_LDAP_GROUP')
    UTH_LDAP_GROUP_SEARCH = LDAPSearch(
        AUTH_LDAP_GROUP, ldap.SCOPE_SUBTREE, "(objectClass=Group)")
    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")
    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_staff": config('IS_STAFF').decode('utf-8')
    }

    # Populate the Django user from the LDAP directory.
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": config('AUTH_LDAP_USER_ATTR_MAP_FN'),
        "last_name": config('AUTH_LDAP_USER_ATTR_MAP_LN'),
        "email": config('AUTH_LDAP_USER_ATTR_MAP_EMAIL')
    }

    # Populate the Django user_profile from the LDAP directory.
    AUTH_LDAP_PROFILE_ATTR_MAP = {
        "nome_completo": config('AUTH_LDAP_PROFILE_ATTR_MAP_NC')
    }

    # Use LDAP group membership to calculate group permissions.
    AUTH_LDAP_FIND_GROUP_PERMS = config(
        'AUTH_LDAP_FIND_GROUP_PERMS', cast=bool)
    AUTH_LDAP_MIRROR_GROUPS = config('AUTH_LDAP_MIRROR_GROUPS', cast=bool)

    # Cache group memberships for an hour to minimize LDAP traffic
    AUTH_LDAP_CACHE_GROUPS = config('AUTH_LDAP_CACHE_GROUPS', cast=bool)
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = config(
        'AUTH_LDAP_GROUP_CACHE_TIMEOUT', cast=int)

    AUTH_PROFILE_MODULE = config('AUTH_PROFILE_MODULE')

    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',) + AUTHENTICATION_BACKENDS


# PENTAHO
PENTAHO_SERVER = config('PENTAHO_SERVER')
PENTAHO_USERNAME_PASSWORD = config('PENTAHO_USERNAME_PASSWORD', cast=split)

PENTAHO_DASHBOARDS = [
    id_path_filename.split(':')
    for id_path_filename in config('PENTAHO_DASHBOARDS', cast=Csv())]
PENTAHO_DASHBOARDS = {
    id: {'solution': 'public',
         'path': path,
         'file': filename + '.wcdf',
         } for id, path, filename in PENTAHO_DASHBOARDS}


SABERES_URL = config('SABERES_URL')
SABERES_TOKEN = config('SABERES_TOKEN')

print '##########################################################'
print '#### DATABASE: ' + DATABASES['default']['HOST']
print '##########################################################'
