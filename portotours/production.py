import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path)


def gettext_noop(s):
    return s


SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = [*os.environ.get("ALLOWED_HOSTS").split(',')]
BASE_ENDPOINT = os.environ.get('BASE_ENDPOINT')
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.gis',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd parties
    'dotenv',
    'sass_processor',
    'ckeditor',
    'ckeditor_uploader',
    'storages',
    'schedule',
    'crispy_forms',
    'crispy_bootstrap5',
    'bootstrap_datepicker_plus',
    'celery',
    'django_celery_beat',
    'django_celery_results',
    'djcelery_email',
    # local
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'attractions.apps.AttractionsConfig',
    'destinations.apps.DestinationsConfig',
    'purchases.apps.PurchasesConfig',
    'blogs.apps.BlogsConfig',
    'reviews.apps.ReviewsConfig',
    'home.apps.HomeConfig',
]
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
SESSION_COOKIE_AGE = 60 * 60  # 60 minutes
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('CACHES_LOCATION'),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": os.environ.get('CACHES_KEY_PREFIX'),
    },
}
ROOT_URLCONF = 'portotours.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.navbar_context',
            ],
        },
    },
]
WSGI_APPLICATION = 'portotours.wsgi.application'
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get('DB_HOST'),
        "PORT": os.environ.get('DB_PORT'),
    },
    "other": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "postgres",
        "USER": "admin",
    },
}
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
LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ("en", gettext_noop("English")),
    ("en-au", gettext_noop("Australian English")),
    ("en-gb", gettext_noop("British English")),
    ("es", gettext_noop("Spanish")),
    ("fr", gettext_noop("French")),
    ("pt", gettext_noop("Portuguese")),
]
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGGING_FILE = os.environ.get('LOGGING_FILE', 'portotours.log')
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {'format': '[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'},
        "simple": {"format": "[%(asctime)s] %(levelname)s %(message)s"},
    },
    "handlers": {
        "log_to_stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "log_to_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "simple",
            "filename": LOGGING_FILE,
        },
    },
    "loggers": {
        "django": {
            "handlers": [
                "log_to_stdout",
                "log_to_file"
            ],
            "level": "INFO",
            "propagate": True,
        },
        "products": {
            "handlers": [
                "log_to_stdout",
                "log_to_file"
            ],
            "level": "INFO",
            "propagate": False,
        },
        "purchases": {
            "handlers": [
                "log_to_stdout",
                "log_to_file"
            ],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": [
                "log_to_stdout",
                "log_to_file"
            ],
            "level": "INFO",
            "propagate": False,
        },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        # }
    }
}
AUTH_USER_MODEL = 'accounts.User'
LOGOUT_REDIRECT_URL = '/en/'
LOGIN_REDIRECT_URL = '/en/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
)
SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(BASE_DIR, 'static/custom_css'),
]
SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_ROOT = BASE_DIR / 'static'
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'height': 300,
        'width': 800,

        'toolbar_Custom': [
            {'name': 'styles', 'items': ['Styles', 'Format']},
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'source', 'items': ['Source']},
        ],

    }
}
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    }
}
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
BOOKING_MINUTES = 30
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
ADMIN_EMAIL = [('Admin Name', 'admin@example.com')]
MANAGER_EMAIL = ADMIN_EMAIL + [('Manager Name', 'manager@example.com')]
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SITE_NAME = 'onedaytours.pt'
# PROTOCOL = 'https'
DOMAIN = os.environ.get('DOMAIN_NAME', 'localhost:8000')
NAVBAR_CONTEXT_CACHE_TIMEOUT = 3600
CELERY_IMPORTS = (
    "products.tasks",
)
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_CACHE_BACKEND = 'default'
CELERY_RESULT_EXTENDED = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERY_BEAT_SCHEDULE = {
    'check-expired-products': {
        'task': 'products.tasks.check_expired_products',
        'schedule': 60,  # Run every minute
    },
}
