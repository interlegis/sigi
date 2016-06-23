# -*- coding: utf-8 -*-
"""
Django settings for sigi project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import dirname

import django.conf.global_settings as DEFAULT_SETTINGS

BASE_DIR = dirname(dirname(dirname(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

ALLOWED_HOSTS = []

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

SITE_ID = 1

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + [
    'django.core.context_processors.request',
]

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    )

# Database routers
DATABASE_ROUTERS = ['moodlerouter.MoodleRouter', ]

# Application definition
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
    'sigi.apps.whois',

    'sigi.apps.crud',
    'sigi.apps.usuarios',
    'sigi.apps.solicitacoes',

    # Integração com Saberes (moodle)
    'sigi.apps.mdl',
    'sigi.apps.saberes',

    # Third-party apps
    'localflavor',
    'reporting',
    'django_extensions',
    'easy_thumbnails',
    'image_cropping',
    'rest_framework',

    'captcha',
    'crispy_forms',
    'djangobower',
    'floppyforms',
    'sass_processor',

)

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sigi.urls'
WSGI_APPLICATION = 'sigi.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
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
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'sigiStatic'),
)

SERVER_EMAIL = 'sigi@interlegis.leg.br'
DEFAULT_FROM_EMAIL = 'spdt@interlegis.leg.br'
EMAIL_SUBJECT_PREFIX = u'[SIGI]'


EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.interlegis.leg.br'
EMAIL_HOST_USER = 'sapl-test'
EMAIL_HOST_PASSWORD = '2BhCwbGHcZ'
EMAIL_SEND_USER = 'atendimento@interlegis.leg.br'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# LOGIN_REDIRECT_URL = ''
# LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/?next='

# Using pytest directly (without a test runner)
TEST_RUNNER = None

from easy_thumbnails.conf import Settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS

THUMBNAIL_ALIASES = {
    '': {
        'small': {'size': (300, 225), 'crop': True, },
        'thumb': {'size': (160, 120), 'crop': True, },
        'portrait': {'size': (73,100), 'crop': True},
        'icon': {'size': (36,50), 'crop': True},
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

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
    'sass_processor.finders.CssFinder',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap3'
CRISPY_FAIL_SILENTLY = False

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'bower')
BOWER_INSTALLED_APPS = (
    'bootstrap-sass#3.3.6',
    'components-font-awesome#4.5.0',
    'tinymce#4.3.3',
    'jquery-ui#1.11.4',
    'jquery-runner#2.3.3',
    'jQuery-Mask-Plugin#1.13.4',
    'jsdiff#2.2.1',
)

# Additional search paths for SASS files when using the @import statement
SASS_PROCESSOR_INCLUDE_DIRS = (
    os.path.join(BOWER_COMPONENTS_ROOT, 'bower_components'),
    os.path.join(BOWER_COMPONENTS_ROOT, 'bootstrap-sass'),
    os.path.join(BOWER_COMPONENTS_ROOT, 'assets'),
    os.path.join(BOWER_COMPONENTS_ROOT, 'stylesheets'),
)

SABERES_REST_PATH = 'webservice/rest/server.php'
OSTICKET_URL = 'https://suporte.interlegis.leg.br/scp/tickets.php?a=search&query=%s'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# Lista de endereços IP que podem acessar a API de whois
WHOIS_WHITELIST = [
        '127.0.0.1',
        ]
