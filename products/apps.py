from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        # Import signals only after apps are ready, not during app initialization
        # This prevents model loading before migrations complete
        try:
            import products.signals  # noqa
        except Exception as e:
            # Log but don't fail if signals can't be imported during migrations
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Signals import during app startup: {e}")
