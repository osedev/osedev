from .common import *

DEBUG = True

ALLOWED_HOSTS = ['localhost']

GEOCODE_ENABLED = os.environ.get('GEOCODE_ENABLED', False)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

STATICFILES_DIRS += (
    ('dart/src', 'ose/dart/web'),
)

DATABASES['default'].update({
    'NAME': 'ose_local',
    'PORT': '5433'
})
