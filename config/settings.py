"""
Django settings for the Smart Thermostat project.
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-replace-this-with-a-real-secret-key-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
# Note: When using a custom user model, the app that defines the model must be
# listed before ``django.contrib.auth`` and ``django.contrib.admin`` to avoid
# migration ordering issues. See https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#substituting-a-custom-user-model
INSTALLED_APPS = [
    # Local apps (custom user must come before auth and admin)
    'authentication',

    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third‑party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Celery Beat for periodic task scheduling
    'django_celery_beat',

    # Local apps
    'thermostats',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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

# Custom user model
AUTH_USER_MODEL = 'authentication.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Smart Thermostat settings
# ---------------------------------------------------------------------------
# The default timezone for the project is UTC, but individual properties can set
# their own timezone via the `timezone` field on the Property model.
DEFAULT_PROPERTY_TIME_ZONE = os.getenv('DEFAULT_PROPERTY_TIME_ZONE', 'America/Chicago')

# Scheduling defaults (in hours).  These control how many hours before a guest
# arrives we start conditioning the property and how many hours after checkout
# we keep the HVAC system in occupied mode before switching to an eco setting.
PRE_ARRIVAL_HOURS = int(os.getenv('PRE_ARRIVAL_HOURS', '2'))
POST_CHECKOUT_HOURS = int(os.getenv('POST_CHECKOUT_HOURS', '2'))

# Default target temperatures (in Fahrenheit).  These values are used when no
# per‑property overrides are configured.  They can be customised via
# environment variables at deployment time.
DEFAULT_COOL_TEMP = float(os.getenv('DEFAULT_COOL_TEMP', '72'))   # occupied cooling
DEFAULT_HEAT_TEMP = float(os.getenv('DEFAULT_HEAT_TEMP', '68'))   # occupied heating
DEFAULT_ECO_COOL_TEMP = float(os.getenv('DEFAULT_ECO_COOL_TEMP', '78'))  # eco cooling
DEFAULT_ECO_HEAT_TEMP = float(os.getenv('DEFAULT_ECO_HEAT_TEMP', '62'))  # eco heating

# ---------------------------------------------------------------------------
# Celery configuration
#
# We integrate Celery as a task queue to schedule thermostat actions.  In a
# development environment, the broker and result backend default to an in‑memory
# RPC transport.  In production you should set these to use a persistent
# service such as Redis or RabbitMQ via environment variables.
#
# Example for Redis:
#   CELERY_BROKER_URL=redis://redis:6379/0
#   CELERY_RESULT_BACKEND=redis://redis:6379/1
#
# Celery settings are namespaced by the `CELERY_` prefix, which allows us to
# call `app.config_from_object('django.conf:settings', namespace='CELERY')`
#
# We also define a beat schedule that periodically scans calendar events and
# schedules pre‑arrival and post‑checkout actions.
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'memory://')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'rpc://')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'scan-calendar-events-every-hour': {
        'task': 'thermostats.tasks.scan_calendar_events',
        'schedule': crontab(minute=0, hour='*'),
    },
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development only, restrict in production
