"""
Django base settings for sigi project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Application definition

INSTALLED_APPS = [
    'sigi.apps.casas',
    'sigi.apps.contatos',
    'sigi.apps.convenios',
    'sigi.apps.eventos',
    'sigi.apps.home',
    'sigi.apps.inventario',
    'sigi.apps.ocorrencias',
    'sigi.apps.servicos',
    'sigi.apps.servidores',
    'sigi.apps.utils',
    'localflavor',
    'import_export',
    'tinymce',
    'django_bootstrap5',
    'django.forms',
    'material',
    'material.admin',
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sigi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'sigi.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static",]
STATIC_ROOT = '/var/www/sigi/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django import-export settings
# https://django-import-export.readthedocs.io/en/latest/installation.html#settings

IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = True

# Django Material Admin settings
# https://github.com/MaistrenkoAnton/django-material-admin#django-material-administration

MATERIAL_ADMIN_SITE = {
    'HEADER':  _('SIGI - Sistema de Informações do Interlegis'),
    'TITLE':  _('SIGI'),
    'FAVICON':  'img/favicon.ico',
    # 'MAIN_BG_COLOR':  'color',  # Admin site main color, css color should be specified
    # 'MAIN_HOVER_COLOR':  'color',  # Admin site main hover color, css color should be specified
    'PROFILE_PICTURE':  'img/interlegis.jpeg',  # Admin site profile picture (path to static should be specified)
    'PROFILE_BG':  'img/engitec.jpeg',  # Admin site profile background (path to static should be specified)
    'LOGIN_LOGO':  'img/interlegis.jpeg',  # Admin site logo on login page (path to static should be specified)
    'LOGOUT_BG':  'img/engitec.jpeg',  # Admin site background on login/logout pages (path to static should be specified)
    'SHOW_THEMES':  False,  #  Show default admin themes button
    'TRAY_REVERSE': False,  # Hide object-tools and additional-submit-line by default
    'NAVBAR_REVERSE': False,  # Hide side navbar by default
    # 'SHOW_COUNTS': True, # Show instances counts for each model
    # 'APP_ICONS': {  # Set icons for applications(lowercase), including 3rd party apps, {'application_name': 'material_icon_name', ...}
    #     'sites': 'send',
    # },
    # 'MODEL_ICONS': {  # Set icons for models(lowercase), including 3rd party models, {'model_name': 'material_icon_name', ...}
    #     'site': 'contact_mail',
    # }
}

# SIGI specific settings

MENU_FILE = BASE_DIR / 'settings/menu_conf.yaml'