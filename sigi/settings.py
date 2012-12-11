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

import os
import ldap
import logging

from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

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

DEFAULT_FROM_EMAIL = 'sesostris@interlegis.leg.br'
EMAIL_SUBJECT_PREFIX = u'[SIGI]'
EMAIL_HOST = 'smtp.interlegis.leg.br'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
#EMAIL_USE_TLS = True

DATABASE_ENGINE = 'postgresql_psycopg2'
#DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'sigi'
#DATABASE_NAME = 'devel.db'
DATABASE_USER = 'sigi'
DATABASE_PASSWORD = '123456'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'

TIME_ZONE = 'Brazil/East'
LANGUAGE_CODE = 'pt-br'
DEFAULT_CHARSET = 'utf-8'
SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/sigi/media/'
ADMIN_MEDIA_PREFIX = '/sigi/admin_media/'

# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldap://w2k3dc01.interlegis.gov.br"
AUTH_LDAP_BIND_DN = u"cn=sigi-ldap,ou=Usuários de Sistema,ou=Usuários,ou=Interlegis,dc=interlegis,dc=gov,dc=br"
AUTH_LDAP_BIND_PASSWORD = "Sigi2609"
AUTH_LDAP_USER = u"ou=SINTER,ou=Usuários,ou=Sede,dc=interlegis,dc=gov,dc=br"
AUTH_LDAP_USER_SEARCH = LDAPSearch(AUTH_LDAP_USER, ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")

# Set up the basic group parameters.
AUTH_LDAP_GROUP = "ou=Grupos Organizacionais,ou=Sede,dc=interlegis,dc=gov,dc=br"
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(AUTH_LDAP_GROUP, ldap.SCOPE_SUBTREE, "(objectClass=Group)")
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

# Only users in this group can log in.
#AUTH_LDAP_REQUIRE_GROUP = u"cn=Acesso ao SIGI,ou=Grupos de Permissão,ou=Sede,dc=interlegis,dc=gov,dc=br"

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
  "is_staff": u"cn=Acesso ao SIGI,ou=Grupos de Permissão,ou=Sede,dc=interlegis,dc=gov,dc=br"
}

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
  "first_name": "givenName",
  "last_name": "sn",
  "email": "userPrincipalName"
}

# Populate the Django user_profile from the LDAP directory.
AUTH_LDAP_PROFILE_ATTR_MAP = {
  "nome_completo": "cn"
}

#AUTH_LDAP_PROFILE_FLAGS_BY_GROUP = {
#  "is_awesome": "cn=awesome,ou=django,ou=groups,dc=example,dc=com",
#}

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_MIRROR_GROUPS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

AUTH_PROFILE_MODULE = 'servidores.Servidor'

# Keep ModelBackend around for per-user permissions and maybe a local superuser.
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

CACHE_BACKEND = 'locmem://' # Considerar seriamente a possibilidade de usar o memcached
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
