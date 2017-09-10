from .common import *

ALLOWED_HOSTS = ['sandbox.osedev.org']

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES['default'].update({
    'NAME': 'ose_sandbox',
    'HOST': 'postgres',
    'USER': 'postgres',
})
