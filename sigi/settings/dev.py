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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'moodle.db'),
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

PENTAHO_SERVER = 'http://localhost.com/pentaho/'
PENTAHO_DASHBOARDS = ('saberes',)
PENTAHO_USERNAME_PASSWORD = 'root@root'

SABERES_URL = 'http://your-moodle-url.com'
SABERES_TOKEN = 'token-generated-by-moodle-to-access-webservice-api'
