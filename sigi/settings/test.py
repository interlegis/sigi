from base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0$ip1fb5xtq%a=)-k_4r^(#jn0t^@+*^kihkxkozg-mip7+w3+'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sigi',  # will be actually used as "test_sigi" by pytest-django
        'USER': 'sigi',
        'PASSWORD': 'sigi',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Validate arguments in django-dynamic-fixture
# http://django-dynamic-fixture.readthedocs.org/en/latest/more.html?highlight=ddf_validate_args#validate-arguments-new-in-1-5-0
DDF_VALIDATE_ARGS = True
DDF_DEBUG_MODE = True
DDF_DEFAULT_DATA_FIXTURE = 'sigi.testutils.SigiDataFixture'
