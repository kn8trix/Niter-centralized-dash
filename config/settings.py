"""Django settings for the Niter Centralized Dash portal.

Configuration is environment-driven: secrets and deployment-specific values
are read from environment variables (optionally sourced from a local ``.env``
file — see ``.env.example``). A missing/mis-set environment can never
accidentally run the site in debug mode: ``DEBUG`` hard-defaults to ``False``
and must be explicitly enabled.

Real environment variables always take precedence over ``.env`` values, so
production deployments can inject secrets via their process manager without
touching the repository.
"""

import logging
import os
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Environment -----------------------------------------------------------------
# Reads ``.env`` when present (dev convenience); existing OS environment
# variables win, so nothing in ``.env`` can override a real environment value.
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
)
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    environ.Env.read_env(str(_env_file))

# Hard default to False — production must opt into DEBUG explicitly.
DEBUG = env('DEBUG')

SECRET_KEY = env('SECRET_KEY', default='')
if DEBUG:
    # Local convenience: a fresh checkout runs without a .env. The fallback
    # key is dev-only and never used in production.
    SECRET_KEY = SECRET_KEY or 'django-insecure-niter-centralized-dash-dev-key'
elif not SECRET_KEY:
    if env.bool('RENDER_BUILD', default=False):
        # Build phase only: ``build.sh`` runs ``collectstatic`` and ``migrate``
        # before the service's generated SECRET_KEY is injected, so those
        # steps must not crash on a not-yet-loaded env var. The throwaway
        # placeholder is used solely here — the runtime start command never
        # sets RENDER_BUILD, so a genuinely missing secret still fails closed
        # below when the app actually boots.
        logger.warning(
            'SECRET_KEY not set during build — using a throwaway build-only '
            'placeholder for collectstatic/migrate.'
        )
        SECRET_KEY = 'django-insecure-render-build-only-placeholder'
    else:
        # Fail closed: a production deploy without a secret must not silently
        # run with a known, published key.
        raise ImproperlyConfigured(
            'SECRET_KEY must be set (via environment or .env) when DEBUG is False.'
        )

# Comma-separated in .env, e.g. "niter.edu.bd,www.niter.edu.bd"
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Optional: comma-separated origins allowed to POST with CSRF protection
# (needed when the site sits behind a proxy on a custom domain).
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')

# --- Render PaaS auto-config (render.yaml Blueprint) --------------------------
# Render injects ``RENDER=true`` for every service it runs. The public hostname
# is auto-generated (``<service>.onrender.com``) and not known in advance, so
# we append the platform domain to the env-driven host list and trust CSRF for
# its origin. The production custom domain (niter.edu.bd) is included here too,
# matching the ``domains:`` entry in render.yaml. Any additional hosts can still
# be injected via the ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS environment
# variables — this block only ever appends, never replaces.
if env.bool('RENDER', default=False):
    for _host in (
        '.onrender.com',
        'niter.edu.bd',
        'www.niter.edu.bd',
        'localhost',
        '127.0.0.1',
    ):
        if _host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(_host)
    _csrf_origins = env('CSRF_TRUSTED_ORIGINS')
    for _origin in (
        'https://*.onrender.com',
        'https://niter.edu.bd',
        'https://www.niter.edu.bd',
    ):
        if _origin not in _csrf_origins:
            _csrf_origins.append(_origin)
    CSRF_TRUSTED_ORIGINS = _csrf_origins

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
    # WhiteNoise serves collected static assets in production without a
    # separate web server — must sit right after SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Sends the X-Frame-Options: DENY header (paired with X_FRAME_OPTIONS below).
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
                # Published builder pages flagged for the top navigation
                'core.context_processors.custom_pages_nav',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Real-time notification engine — Django Channels ASGI application
ASGI_APPLICATION = 'config.asgi.application'

# --- Database --------------------------------------------------------------------
# ``DATABASE_URL`` (e.g. ``postgres://user:pass@host:5432/dbname``) drives
# production; unset falls back to the local SQLite file for dev/tests.
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///%s' % (BASE_DIR / 'db.sqlite3')),
}

# django.contrib.sites — required by allauth social accounts
SITE_ID = 1

# Google OAuth (allauth) — Phase 1
# Scopes request openid/profile/email plus Google Drive (app-data + read-only
# browsing) and Sheets access; AUTH_PARAMS request an offline refresh token so
# long-lived tokens can be stored for background Drive/Sheets operations.
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'openid',
            'profile',
            'email',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/spreadsheets',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
            # Forces the consent screen on every authorization, which guarantees
            # Google returns a fresh refresh token (also on re-connect flows)
            # for background Drive/Sheets operations.
            'prompt': 'consent',
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Static & media ---------------------------------------------------------------
STATIC_URL = '/static/'

# Global stylesheets (theme.css) served from this directory
STATICFILES_DIRS = [BASE_DIR / 'static']

# Collected assets live here (``collectstatic``); WhiteNoise serves them.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise backend: compresses and adds cache headers to collected files.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}
# WhiteNoise auto-enables USE_FINDERS/AUTOREFRESH while DEBUG=True, so static
# edits appear immediately in development without re-running collectstatic.

# User-uploaded files (CourseMaterial documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Real-time channel layer ------------------------------------------------------
# channels_redis when a reachable ``REDIS_URL`` is configured (multi-worker
# production); otherwise the in-memory layer so single-process dev, tests, and
# Redis-less deployments keep working. The startup probe is cheap (1.5s
# timeouts) and a Redis outage after startup degrades to "no live push" rather
# than an error — see ``core.consumers.notify_user``.
def _default_channel_layer():
    redis_url = env('REDIS_URL', default='')
    if not redis_url:
        return {'BACKEND': 'channels.layers.InMemoryChannelLayer'}
    try:
        import redis as redis_client
        probe = redis_client.Redis.from_url(
            redis_url,
            socket_connect_timeout=1.5,
            socket_timeout=1.5,
        )
        probe.ping()
    except Exception:
        import logging
        logging.getLogger('config.settings').warning(
            'Redis unreachable at %s — falling back to the in-memory channel layer.',
            redis_url,
        )
        return {'BACKEND': 'channels.layers.InMemoryChannelLayer'}
    return {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [redis_url]},
    }


CHANNEL_LAYERS = {'default': _default_channel_layer()}

# --- Authentication ---------------------------------------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# --- Security ---------------------------------------------------------------------
X_FRAME_OPTIONS = 'DENY'

# Production hardening is only meaningful with DEBUG off; each flag can still
# be overridden via the environment for proxy setups.
if not DEBUG:
    # Redirect all plain-HTTP traffic to HTTPS (behind a terminating proxy,
    # SECURE_PROXY_SSL_HEADER keeps redirect detection correct).
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Cookies are only sent over HTTPS.
    SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
    CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
    # HSTS: force HTTPS for a year, including subdomains + preload list.
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Send a restrictive Referrer-Policy header on responses.
    SECURE_REFERRER_POLICY = 'same-origin'
