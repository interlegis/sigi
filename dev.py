# -*- coding: utf-8 -*-

from base import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0$ip1fb5xtq%a=)-k_4r^(#jn0t^@+*^kihkxkozg-mip7+w3+'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sigi',
        'USER': 'sigi',
        'PASSWORD': '123456',
        'HOST': 'localhost',
    },
    'moodle': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'moodledemo',
        'USER': 'saberesdemo',
        'PASSWORD': 'UX72kn3gCIf4GiJaKASu',
        'HOST': 'bdinterlegis.interlegis.leg.br',
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TEMPLATE_CONTEXT': True,
}

INSTALLED_APPS += (
    'debug_toolbar',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# PENTAHO
PENTAHO_SERVER = 'pentaho01a.interlegis.leg.br:8080'
PENTAHO_USERNAME_PASSWORD = ('sigi', 'sigi')

PENTAHO_DASHBOARDS = (
    # (id, path, filename)
    ('saberes-geral', 'saberes', 'geral'),
    ('saberes-cursos-sem-tutoria', 'saberes', 'cursos sem tutoria'),
    ('saberes-cursos-com-tutoria', 'saberes', 'cursos com tutoria'),
)

PENTAHO_DASHBOARDS = {
    id: {
        'solution': 'public',
        'path': path,
        'file': filename + '.wcdf',
    } for id, path, filename in PENTAHO_DASHBOARDS}

SABERES_URL = 'http://saberesdemo.interlegis.leg.br'
SABERES_TOKEN = '5e80515d30c4e9a41680ffe0029079fe'

# Baseline configuration.

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

AUTH_LDAP_SERVER_URI = "ldap://w2k3dc01.interlegis.gov.br"
AUTH_LDAP_BIND_DN = u"cn=sigi-ldap,ou=Usuários de Sistema,ou=Usuários,ou=Interlegis,dc=interlegis,dc=gov,dc=br"
AUTH_LDAP_BIND_PASSWORD = "Sigi2609"
AUTH_LDAP_USER = u"ou=SINTER,ou=Usuários,ou=Sede,dc=interlegis,dc=gov,dc=br"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    AUTH_LDAP_USER, ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")

# Set up the basic group parameters.
AUTH_LDAP_GROUP = "ou=Grupos Organizacionais,ou=Sede,dc=interlegis,dc=gov,dc=br"
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    AUTH_LDAP_GROUP, ldap.SCOPE_SUBTREE, "(objectClass=Group)")
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

# AUTH_LDAP_PROFILE_FLAGS_BY_GROUP = {
#  "is_awesome": "cn=awesome,ou=django,ou=groups,dc=example,dc=com",
#}

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_MIRROR_GROUPS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

AUTH_PROFILE_MODULE = 'servidores.Servidor'
