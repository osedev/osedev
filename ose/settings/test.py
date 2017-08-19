from .common import *

ALLOWED_HOSTS = ['osedev.localhost']

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DATABASES['default'].update({
    'NAME': 'ose_test',
    'HOST': 'postgres',
    'USER': 'postgres',
})

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
