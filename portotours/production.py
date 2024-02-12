from .settings import *  # noqa

ALLOWED_HOSTS = [*os.environ.get("ALLOWED_HOSTS").split(',')]
BASE_ENDPOINT = os.environ.get('BASE_ENDPOINT')
DEBUG = False

# WhiteNoise configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add whitenoise middleware after the security middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

SECRET_KEY = os.environ.get('SECRET_KEY')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('CACHES_LOCATION'),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": os.environ.get('CACHES_KEY_PREFIX'),
    },
}

# DigitalOcean Spaces
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    }
}
