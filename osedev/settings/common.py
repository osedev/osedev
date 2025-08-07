import os, sys

SECRET_KEY = os.environ.get('SECRET_KEY', 'abc123')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

DEBUG = False

SITE_ID = 1

ALLOWED_HOSTS = []

GEOCODE_ENABLED = False

BROKER_URL = 'amqp://guest:guest@rabbitmq:5672//'
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_ipc.IPCChannelLayer",
        "ROUTING": "osedev.routing.channel_routing",
        "CONFIG": {
            "prefix": "osedev",
        },
    },
}

# Application definition

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '../'))

AUTH_USER_MODEL = 'user.User'
X_FRAME_OPTIONS = 'ALLOW'
LOGIN_REDIRECT_URL = '/'

EMAIL_HOST = 'mail'
DEFAULT_FROM_EMAIL = 'OSEDev <hr@osedev.org>'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
#    'allauth.socialaccount.providers.google',
#    'allauth.socialaccount.providers.facebook',
#    'allauth.socialaccount.providers.github',
#    'allauth.socialaccount.providers.openid',
    'osedev.lib',
    'osedev.apps.user',
    'osedev.apps.main',
    'osedev.apps.notebook',
    'osedev.apps.onboarding',
    'osedev.apps.plm',
    'osedev.apps.chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'osedev.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'osedev.apps.main.context_processors.ose',
            ],
        },
    },
]

WSGI_APPLICATION = 'osedev.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'TEST': {
            'SERIALIZE': False
        }
    },
}


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Django Allauth Configuration
# http://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = "osedev.apps.user.account.AccountAdapter"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_USERNAME_BLACKLIST = (
    'auth', 'account', 'accounts', 'user', 'users', 'settings', 'password',
    'admin', 'main', 'notebook', 'notebooks', 'onboarding', 'site', 'wiki', 'task', 'tasks',
    'app', 'activity', 'graph', 'graphs', 'report', 'reports',
)
ACCOUNT_USERNAME_MIN_LENGTH = 2
SOCIALACCOUNT_ADAPTER = "osedev.apps.user.account.SocialAccountAdapter"

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Central'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '..', 'static'))

STATICFILES_DIRS = (
    'osedev/static',
)


TESTING = 'test' in sys.argv

if TESTING:

    class DisableMigrations:

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()

    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
