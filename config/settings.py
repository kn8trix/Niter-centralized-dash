import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-niter-centralized-dash-dev-key'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Daphne must be first so runserver serves ASGI (HTTP + WebSockets)
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Real-time notification engine (WebSockets)
    'channels',

    # Google OAuth (allauth) — Phase 1
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                # Expose the authenticated user ({{ user }}) to every template
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Centralized endpoint registry for decoupled URL mappings
                'core.context_processors.endpoints',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Real-time notification engine — Django Channels ASGI application
ASGI_APPLICATION = 'config.asgi.application'

# In-memory channel layer: fine for single-process dev + tests. Swap for
# channels_redis in production (multi-worker) deployments.
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# django.contrib.sites — required by allauth social accounts
SITE_ID = 1

# Google OAuth (allauth) — Phase 1
# Scopes request profile/email plus Google Drive (app-data only) and Sheets
# access; AUTH_PARAMS request a refresh token (offline + consent) so long-lived
# tokens can be stored in GoogleUserToken for the notes/club backends.
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
            'prompt': 'consent',
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'

# Global stylesheets (theme.css) served from this directory
STATICFILES_DIRS = [BASE_DIR / 'static']

# Authentication
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
