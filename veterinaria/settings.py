from pathlib import Path
from urllib.parse import urlparse
import os
import socket

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-vet-sistema-2026-secret-key-change-in-production')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1', 'http://localhost:8080', 'http://127.0.0.1:8080', 'https://localhost', 'https://127.0.0.1']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    # Local apps
    'apps.core',
    'apps.clientes',
    'apps.agenda',
    'apps.medico',
    'apps.inventario',
    'apps.facturacion',
    'apps.grooming',
    'apps.reportes',
    'apps.telemedicina',
    'apps.usuarios',
    'apps.configuracion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.clientes.middleware.PortalClienteMiddleware',
]

ROOT_URLCONF = 'veterinaria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.configuracion.context_processors.configuracion',
            ],
        },
    },
]

WSGI_APPLICATION = 'veterinaria.wsgi.application'

if os.environ.get('DB_ENGINE', 'mysql') == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'sistema_veterinaria_db'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Guatemala'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')


def _redis_disponible(url):
    try:
        import redis
        destino = urlparse(url)
        with socket.create_connection((destino.hostname or '127.0.0.1', destino.port or 6379), timeout=0.3):
            return True
    except Exception:
        return False


REDIS_ACTIVO = _redis_disponible(REDIS_URL)

if REDIS_ACTIVO:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'vetsystem',
            'TIMEOUT': 300,
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'vetsystem',
        }
    }

SILENCED_SYSTEM_CHECKS = ['models.W036']

LOGIN_URL = '/login/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 8
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ─── django-allauth OAuth / Google ───────────────────────────────────────────
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Autenticación clásica de Django (usuario/contraseña)
    'django.contrib.auth.backends.ModelBackend',
    # Autenticación de allauth (OAuth / Social)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Comportamiento de allauth (sintaxis v65+)
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['username*', 'email', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'   # sin verificación por email
SOCIALACCOUNT_AUTO_SIGNUP = True       # crear cuenta automáticamente al hacer login con Google
SOCIALACCOUNT_LOGIN_ON_GET = True      # no pide confirmación extra

# Redirigir después del login social
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'

# Scopes de Google solicitados
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': '',
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    }
}


MICROSERVICES_HOST = os.environ.get('MICROSERVICES_HOST', '127.0.0.1')

try:
    from .local_settings import *
except ImportError:
    pass
