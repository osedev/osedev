from .common import *

GEOCODE_ENABLED = True

ALLOWED_HOSTS = ['osedev.org']

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES['default'].update({
    'NAME': 'ose_production',
    'HOST': 'postgres',
    'USER': 'postgres',
})
