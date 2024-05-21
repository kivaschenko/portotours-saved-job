"""
Django settings for portotours project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# dotenv
dotenv_path = Path(__file__).resolve().parent.parent / '.dev.env'
load_dotenv(dotenv_path)


# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
def gettext_noop(s):
    return s


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2d18496423377c985535dbcb64e6b9df474f7238fc124315221bbdfb3de7a764'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']  # for debug in CI/CD
BASE_ENDPOINT = 'http://127.0.0.1:8000'  # debug mode for stripe confirmation

# Application definition

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
    'django_extensions',
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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
############
# SESSIONS #
############

# Cache to store session data if using the cache session backend.
SESSION_CACHE_ALIAS = "default"
# Cookie name. This can be whatever you want.
SESSION_COOKIE_NAME = "sessionid"
# Age of cookie, in seconds (default: 2 weeks).
SESSION_COOKIE_AGE = 60 * 60  # minutes
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

#########
# CACHE #
#########

# The cache backends to use.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": os.environ.get('CACHES_LOCATION'),
#         "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
#         "KEY_PREFIX": os.environ.get('CACHES_KEY_PREFIX'),
#     },
# }
CACHE_MIDDLEWARE_KEY_PREFIX = ""
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_ALIAS = "default"

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

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    # "default": {
    #     "ENGINE": "django.contrib.gis.db.backends.postgis",
    #     "NAME": 'postgres',
    #     "USER": 'admin',
    #     "PASSWORD": '112358',
    #     "HOST": 'localhost',
    #     "PORT": '54321',
    # },
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

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

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

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
LOGGING_FILE = os.environ.get('LOGGING_FILE', 'portotours.log')

# Logger
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

# Redirect URLs after login/logout
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Bootstrap Sass
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
)

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(BASE_DIR, 'static/custom_css'),
]

# Set up Sass Processor settings
SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_ROOT = BASE_DIR / 'static'

# For debug mode if platform is macOS
if DEBUG is True:
    import platform

    # Get the system's platform
    current_platform = platform.system()

    # Check if the platform is macOS
    if current_platform == 'Darwin':
        print("The current operating system is macOS. Using another path for GDAL support.")
        GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH', '/opt/homebrew/Cellar/gdal/3.8.5/lib/libgdal.dylib')
        GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH', '/opt/homebrew/Cellar/geos/3.12.1/lib/libgeos_c.dylib')
    else:
        print("The current operating system is not macOS.")

# CKEDITOR
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
# STATICFILES_DIRS = (BASE_DIR / 'static',)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        # "BACKEND": 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        # "BACKEND": 'storages.backends.s3boto3.S3Boto3Storage',
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    }
}

# DigitalOcean Spaces
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com'

# STRIPE credentials
STRIPE_PUBLIC_KEY = 'pk_test_51OgTxhB0X2obciNigcJJ1FZ831YDandrQUaDNTs6OmzaDaXljGs4W5argoWEaRy3brFpaGVeUtcmeRJEPyT8b9sO000V412c4k'
STRIPE_SECRET_KEY = 'sk_test_51OgTxhB0X2obciNiyzPMesPZRql9jQs9pOb2CNmkU8Lf9qYM55iGyBZ5eoTBGFzTQ3xlOl0SdPCp3QIAuems22t500sswKbQDU'

# PROJECT BUSINESS LOGIC
BOOKING_MINUTES = 30

# CRISPY FORMS
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# In your Django settings file (settings.py)
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'service_layer/debug_emails'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'OneDayTours<<info@onedaytours.com>>'

# Default email address to use for various automated messages from Django
DEFAULT_FROM_EMAIL = 'default-email@example.com'

# Additional settings for error reporting emails (optional)
ADMIN_EMAIL = [('Admin Name', 'admin@example.com')]
MANAGER_EMAIL = ADMIN_EMAIL + [('Manager Name', 'manager@example.com')]
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ORDER_EMAIL = 'orders@portotours.pt'

# This params used also in email template for reset password

# Set your site name
SITE_NAME = 'OneDayTours.com'

# Set the protocol (http or https)
PROTOCOL = 'http'

# Set your domain
DOMAIN = os.environ.get('DOMAIN_NAME', 'localhost:8000')

# Navbar top lists cache
NAVBAR_CONTEXT_CACHE_TIMEOUT = 3600

# Celery Configuration Options
CELERY_IMPORTS = (
    "products.tasks",
)
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_CACHE_BACKEND = 'default'
CELERY_RESULT_EXTENDED = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# Use local redis server
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
    }
}
PRODUCT_EXPIRE_MINUTES = 60  # Expire timedelta for Product