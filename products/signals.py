import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from schedule.models import Calendar

from .models import ParentExperience


logger = logging.getLogger(__name__)


@receiver(post_save, sender=ParentExperience)
def create_calendar(sender, instance, created, **kwargs):
    """
    Signal handler function to create a new calendar when a new ParentExperience is created.
    """
    if created:
        # Create a new calendar associated with the new ParentExperience
        calendar_name = f"{instance.parent_name} Calendar"
        calendar = Calendar.objects.get_or_create_calendar_for_object(instance, distinction='experience', name=calendar_name)
        logger.info(f"Created calendar: {calendar_name}")
