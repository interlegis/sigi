from sigi.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sigi-3',
        'USER': 'sigi',
        'PASSWORD': '123456',
        'HOST': 'database',
    },
}