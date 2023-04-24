"""
Django base settings for sigi project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import environ
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from django.conf.locale.pt_BR import formats as br_formats


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

env = environ.Env()
env.read_env(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="Unsafe")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = env("ADMINS", eval)

DATA_UPLOAD_MAX_NUMBER_FIELDS = 3000

# Application definition

INSTALLED_APPS = [
    "sigi.apps.casas",
    "sigi.apps.contatos",
    "sigi.apps.convenios",
    "sigi.apps.eventos",
    "sigi.apps.home",
    "sigi.apps.inventario",
    "sigi.apps.ocorrencias",
    "sigi.apps.parlamentares",
    "sigi.apps.servicos",
    "sigi.apps.servidores",
    "sigi.apps.utils",
    "localflavor",
    "import_export",
    "tinymce",
    "django.forms",
    "material",
    "material.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "sigi.apps.utils.middleware.SigiAlertsMiddleware",
]

if DEBUG:
    INSTALLED_APPS = [
        "debug_toolbar",
    ] + INSTALLED_APPS
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE

EMAIL_PORT = env("EMAIL_PORT", int, default=25)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_SUBJECT_PREFIX = env("EMAIL_SUBJECT_PREFIX", default="[SIGI]")
EMAIL_USE_LOCALTIME = env("EMAIL_USE_LOCALTIME", bool, default=False)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", bool, default=False)
EMAIL_USE_SSL = env("EMAIL_USE_SSL", bool, default=False)
EMAIL_TIMEOUT = env("EMAIL_TIMEOUT", int, default=None)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="sigi@interlegis.leg.br")

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}

ROOT_URLCONF = "sigi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "sigi.apps.utils.context_processors.site_context",
                "sigi.apps.home.context_processors.dashboard",
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "sigi.wsgi.application"


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

if env("AUTH_LDAP_SERVER_URI", default=None):
    AUTHENTICATION_BACKENDS = [
        "django_auth_ldap.backend.LDAPBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]
    from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
    import ldap

    AUTH_LDAP_SERVER_URI = env("AUTH_LDAP_SERVER_URI")
    AUTH_LDAP_BIND_DN = env("AUTH_LDAP_BIND_DN")
    AUTH_LDAP_BIND_PASSWORD = env("AUTH_LDAP_BIND_PASSWORD")
    AUTH_LDAP_USER = env("AUTH_LDAP_USER")
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        AUTH_LDAP_USER, ldap.SCOPE_SUBTREE, env("AUTH_LDAP_USER_SEARCH_STRING")
    )
    AUTH_LDAP_GROUP = env("AUTH_LDAP_GROUP")
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
        AUTH_LDAP_GROUP,
        ldap.SCOPE_SUBTREE,
        env("AUTH_LDAP_GROUP_SEARCH_STRING"),
    )
    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(
        name_attr=env("AUTH_LDAP_GROUP_TYPE_STRING")
    )
    AUTH_LDAP_USER_ATTR_MAP = env("AUTH_LDAP_USER_ATTR_MAP", cast=eval)
    AUTH_LDAP_PROFILE_ATTR_MAP = env("AUTH_LDAP_PROFILE_ATTR_MAP", eval)
    AUTH_LDAP_FIND_GROUP_PERMS = env("AUTH_LDAP_FIND_GROUP_PERMS", bool)
    AUTH_LDAP_MIRROR_GROUPS = env("AUTH_LDAP_MIRROR_GROUPS", bool)
    AUTH_LDAP_CACHE_GROUPS = env("AUTH_LDAP_CACHE_GROUPS", bool)
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = env("AUTH_LDAP_GROUP_CACHE_TIMEOUT", int)
    AUTH_PROFILE_MODULE = env("AUTH_PROFILE_MODULE")

LOGIN_REDIRECT_URL = "home_index"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "../static/"

# Media files
# https://docs.djangoproject.com/en/4.0/topics/files/#managing-files

MEDIA_ROOT = BASE_DIR / "../media"
MEDIA_URL = "media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django import-export settings
# https://django-import-export.readthedocs.io/en/latest/installation.html#settings

IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = True

# Admin date and time short formats for pt_BR
br_formats.DATE_FORMAT = br_formats.SHORT_DATE_FORMAT
br_formats.DATETIME_FORMAT = br_formats.SHORT_DATETIME_FORMAT

# Django Material Admin settings
# https://github.com/MaistrenkoAnton/django-material-admin#django-material-administration

MATERIAL_ADMIN_SITE = {
    "HEADER": _("SIGI - Sistema de Informações do Interlegis"),
    "TITLE": _("SIGI"),
    "FAVICON": "img/favicon.ico",
    "PROFILE_PICTURE": "img/interlegis.jpeg",  # Admin site profile picture (path to static should be specified)
    "PROFILE_BG": "img/engitec.jpeg",  # Admin site profile background (path to static should be specified)
    "LOGIN_LOGO": "img/interlegis.jpeg",  # Admin site logo on login page (path to static should be specified)
    "LOGOUT_BG": "img/engitec.jpeg",  # Admin site background on login/logout pages (path to static should be specified)
    "SHOW_THEMES": False,  #  Show default admin themes button
    "TRAY_REVERSE": False,  # Hide object-tools and additional-submit-line by default
    "NAVBAR_REVERSE": False,  # Hide side navbar by default
}

# tinyMCE rich text editor settings
# https://django-tinymce.readthedocs.io/en/latest/installation.html#configuration

TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "menubar": True,
    "plugins": "table,code,fullscreen,hr,link,lists,advlist,paste,print,searchreplace,visualblocks,visualchars",
    "toolbar1": "undo redo print searchreplace visualblocks visualchars | styleselect fontsizeselect	| bold italic strikethrough subscript superscript underline hr | backcolor forecolor removeformat",
    "toolbar2": "alignleft aligncenter alignright alignjustify | numlist bullist outdent indent | link unlink |fullscreen code",
    "toolbar3": "table tabledelete | tableprops tablerowprops tablecellprops | tableinsertrowbefore tableinsertrowafter tabledeleterow tablerowheader | tableinsertcolbefore tableinsertcolafter tabledeletecol tablecolheader | tablemergecells tablesplitcells | tablecellbackgroundcolor tablecellbordercolor tablecellborderwidth tablecellborderstyle",
}

# SIGI specific settings

MENU_FILE = BASE_DIR / "menu_conf.yaml"
HOSPEDAGEM_PATH = Path(env("HOSPEDAGEM_PATH", default="/tmp/HOSP/"))
REGISTRO_PATH = Path(env("REGISTRO_PATH", default="/tmp/DNS/"))

# Integração com Moodle

MOODLE_BASE_URL = env("MOODLE_BASE_URL", default=None)
MOODLE_API_TOKEN = env("MOODLE_API_TOKEN", default=None)
