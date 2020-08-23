from .base import *

DEBUG = True

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

