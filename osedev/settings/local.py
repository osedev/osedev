from .common import *

DEBUG = True

ALLOWED_HOSTS = ['localhost']

BROKER_URL = 'amqp://guest:guest@localhost:5672//'

GEOCODE_ENABLED = os.environ.get('GEOCODE_ENABLED', False)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DATABASES['default'].update({
    'NAME': 'ose_local',
})
