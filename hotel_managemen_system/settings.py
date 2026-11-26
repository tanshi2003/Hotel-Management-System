import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'development-only-insecure-key-change-me')
DEBUG = os.getenv('DEBUG', 'False').strip().lower() in ('1', 'true', 'yes', 'on')

_default_hosts = 'localhost,127.0.0.1,[::1],hotel-management-system-k8f0.onrender.com'
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', _default_hosts).split(',') if host.strip()]

if not DEBUG and SECRET_KEY == 'development-only-insecure-key-change-me':
    import warnings
    warnings.warn('DJANGO_SECRET_KEY is not configured. Set it before deploying.', RuntimeWarning)

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'user_profile', 'hotel_room', 'room_booking', 'management',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'hotel_managemen_system.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug', 'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'hotel_managemen_system.wsgi.application'
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.config(
        default=DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG
    )}
else:
    # Local development fallback. Production must set DATABASE_URL to a managed DB.
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
_default_csrf_origins = 'https://hotel-management-system-k8f0.onrender.com'
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', _default_csrf_origins).split(',') if origin.strip()]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
AUTH_USER_MODEL = 'user_profile.Account'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = '/hms/user/login/'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
