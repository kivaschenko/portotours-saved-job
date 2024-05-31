import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from schedule.models import Calendar, EventRelation

from .models import ParentExperience, ExperienceEvent, Product


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


@receiver(post_save, sender=ExperienceEvent)
def fill_empty_prices_and_set_relation(sender, instance, created, **kwargs):
    if created:
        # Get ParentExperience obj
        relation = instance.calendar.calendarrelation_set.first()
        parent_experience_obj = relation.content_object
        if not instance.max_participants:
            instance.max_participants = parent_experience_obj.max_participants
        if not instance.booked_participants:
            instance.booked_participants = 0
            instance.remaining_participants = parent_experience_obj.max_participants
        else:
            instance.remaining_participants = instance.max_participants - instance.booked_participants
        if not instance.special_price and not parent_experience_obj.is_private:
            instance.special_price = parent_experience_obj.price
        if not instance.child_special_price and not parent_experience_obj.is_private:
            instance.child_special_price = parent_experience_obj.child_price
        if parent_experience_obj.is_private and not instance.total_price:
            instance.total_price = parent_experience_obj.price
        instance.save()

        # Set event relation
        EventRelation.objects.create(event=instance, content_object=parent_experience_obj, distinction='experience event')


@receiver(post_save, sender=Product)
def apply_second_purchase_discount(sender, instance, created, **kwargs):
    if not created or instance.price_is_special:
        return
    session_key = instance.session_key

    if not session_key:
        return

    product_count = Product.get_products_count(session_key)
    first_product = Product.get_first_product(session_key)

    # If first is the first product, no discount applies
    if product_count == 1:
        return

    # Apply discount for current product
    discount = instance.parent_experience.second_purchase_discount
    if not discount:
        return

    if first_product and instance.id != first_product.id:
        if instance.parent_experience.is_private:
            # Subtract discount from total price for private products
            new_total_price = instance.total_price - discount
            instance.total_price = max(new_total_price, 0)  # Ensure price doesn't go negative
        else:
            # Subtract discount from adult price for group products
            new_adult_price = instance.adults_price - discount
            instance.adults_price = max(new_adult_price, 0)  # Ensure price doesn't go negative

        instance.price_is_special = True
        instance.save()
        logger.info(f"Added second purchase discount: {discount} to Product: {instance}")

