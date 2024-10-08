import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_path = Path(__file__).resolve().parent.parent / '.env.prod'
load_dotenv(dotenv_path)


def gettext_noop(s):
    return s


SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = [*os.environ.get("ALLOWED_HOSTS").split(',')]
# ALLOWED_HOSTS += ['localhost', '127.0.0.1', '[::1]']
BASE_ENDPOINT = os.environ.get('BASE_ENDPOINT')
INSTALLED_APPS = [
    # 'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.gis',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django.contrib.sitemaps',
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
    'corsheaders',
    'django_extensions',
    'compressor',
    # local
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'attractions.apps.AttractionsConfig',
    'destinations.apps.DestinationsConfig',
    'purchases.apps.PurchasesConfig',
    'blogs.apps.BlogsConfig',
    'reviews.apps.ReviewsConfig',
    'home.apps.HomeConfig',
    'landing_pages.apps.LandingPagesConfig',
]
# WhiteNoise configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add whitenoise middleware after the security middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Place CORS middleware here
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'portotours.custom_middleware.IgnoreDisallowedHostMiddleware',  # Add your custom middleware here
    # 'portotours.custom_middleware.ExcludeAdminFromAnalyticsMiddleware',
]

# Cache to store session data if using the cache session backend.
SESSION_CACHE_ALIAS = "default"
# Cookie name. This can be whatever you want.
SESSION_COOKIE_NAME = "sessionid"
# Age of cookie, in seconds (default: 2 weeks).
SESSION_COOKIE_AGE = 60 * 60 * 24  # 24 hours
# A string like "example.com", or None for standard domain cookie.
SESSION_COOKIE_DOMAIN = None
# Whether the session cookie should be secure (https:// only).
SESSION_COOKIE_SECURE = False
# The path of the session cookie.
SESSION_COOKIE_PATH = "/"
# Whether to use the HttpOnly flag.
SESSION_COOKIE_HTTPONLY = True
# Whether to set the flag restricting cookie leaks on cross-site requests.
# This can be 'Lax', 'Strict', 'None', or False to disable the flag.
SESSION_COOKIE_SAMESITE = "Lax"
# Whether to save the session data on every request.
SESSION_SAVE_EVERY_REQUEST = True
# Whether a user's session cookie expires when the web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# The module to store session data
SESSION_ENGINE = "django.contrib.sessions.backends.db"
# Directory to store session files if using the file session module. If None,
# the backend will use a sensible default.
SESSION_FILE_PATH = None
# class to serialize session data
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

# CACHE
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('CACHES_LOCATION'),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": os.environ.get('CACHES_KEY_PREFIX'),
    },
}
CACHE_MIDDLEWARE_SECONDS = 3600  # 1 hour for dynamic content
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
                'home.context_processors.canonical_url',
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
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
    'compressor.finders.CompressorFinder',  # Correct finder for django-compressor
)
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_PRECOMPILERS = [
    ('text/x-scss', 'django_libsass.SassCompiler'),
]

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(BASE_DIR, 'static/custom_css'),
    os.path.join(BASE_DIR, 'static/custom_css/custom.scss')
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
            {'name': 'insert', 'items': ['Image', 'Table', 'SpecialChar']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'source', 'items': ['Source']},
        ],

    }
}
CKEDITOR_RESTRICT_BY_DATE = False
CKEDITOR_RESTRICT_BY_USER = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        # "BACKEND": 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    }
}
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
AWS_DEFAULT_ACL = 'public-read'
# AWS_QUERYSTRING_AUTH = False
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
ORDER_EMAIL = os.environ.get('ORDER_EMAIL')
ADMIN_NAME = os.environ.get('EMAIL_FROM_USER')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
MANAGER_EMAIL = os.environ.get('MANAGER_EMAIL')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SITE_NAME = 'www.onedaytours.pt'
SITE_ID = 1
PROTOCOL = 'https'
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
    'report-about-paid-products': {
        'task': 'products.tasks.report_about_paid',
        'schedule': 90,  # run every 1.5 minutes
    },
}
# SECURE_SSL_REDIRECT = True
PRODUCT_EXPIRE_MINUTES = 60  # Expire timedelta for Product in minutes
CORS_ALLOWED_ORIGINS = [
    'https://onedaytours.pt',
    'https://www.onedaytours.pt',
    # Add other allowed origins as needed
]
CSRF_TRUSTED_ORIGINS = [
    'https://onedaytours.pt',
    'https://www.onedaytours.pt',
]
CORS_ORIGIN_WHITELIST = [
    'https://onedaytours.pt',
    'https://www.onedaytours.pt',
    # Add other allowed origins here if needed
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # You can adjust this value as needed
