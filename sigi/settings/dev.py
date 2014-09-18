from .base import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0$ip1fb5xtq%a=)-k_4r^(#jn0t^@+*^kihkxkozg-mip7+w3+'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sigi.db'),
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'debug_toolbar',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
