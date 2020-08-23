from .base import *

DEBUG = False

ADMINS = (('Özkan', 'ozkancinar95@gmail.com'),)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.path.join(BASE_DIR, 'db.postgresql'),
        'NAME': 'fepisode',
        'USER': 'ozkan',
        'PASSWORD': config['DB']['PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# SECURE_SSL_REDIRECT = True

# SESSION_COOKIE_SECURE = True # Whether to use a secure cookie for the session cookie. If this is set to True,
# the cookie will be marked as “secure”, which means browsers may ensure that the cookie is only sent under an HTTPS connection.

# CSRF_COOKIE_SECURE = True # Whether to use a secure cookie for the CSRF cookie. If this is set to True,
# the cookie will be marked as “secure”, which means browsers may ensure that the cookie is only sent with an HTTPS connection.