# test_settings.py

# Import the original settings from the main settings file
from .settings import STORAGES

# Override the storage backend for staticfiles
STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.StaticFilesStorage"
