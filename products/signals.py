# signals.py

import logging
from decimal import Decimal

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from schedule.models import Calendar, EventRelation

from .models import ParentExperience, ExperienceEvent, Product
from .product_services import create_qrcode_for_product

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

        # New logic to handle occurrences if the instance has a rule
        if instance.rule and instance.end_recurring_period is not None:
            occurrences = instance.get_occurrences(start=instance.effective_start, end=instance.effective_end)
            for occurrence in occurrences:
                # Skip the occurrence if it matches the start and end of the original instance
                if occurrence.original_start == instance.start and occurrence.original_end == instance.end:
                    continue

                new_event = ExperienceEvent(
                    title=instance.title,
                    description=instance.description,
                    calendar=instance.calendar,
                    start=occurrence.original_start,
                    end=occurrence.original_end,
                    max_participants=instance.max_participants,
                    booked_participants=instance.booked_participants,
                    remaining_participants=instance.remaining_participants,
                    special_price=instance.special_price,
                    child_special_price=instance.child_special_price,
                    total_price=instance.total_price,
                    # Copy other necessary fields
                )
                new_event.rule = None
                new_event.save()
                logger.info(f"Event created by signal:\t{new_event}\n")


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
            instance.stripe_price = int(instance.total_price * 100)
        else:
            # Subtract discount from adult price for group products
            new_adult_price = instance.adults_price - discount
            instance.adults_price = max(new_adult_price, 0)  # Ensure price doesn't go negative
            instance.total_price = instance._count_new_total_price()
            instance.stripe_price = int(instance.total_price * 100)

        instance.price_is_special = True
        instance.save()
        logger.info(f"Added second purchase discount: {discount} to Product: {instance}")


@receiver(post_delete, sender=Product)
def adjust_prices_after_delete(sender, instance, **kwargs):
    session_key = instance.session_key

    if session_key:
        products = Product.pending.filter(session_key=session_key).order_by('created_at')

        # Reset discounts for all products
        for product in products:
            if product.parent_experience.is_private:
                product.total_price = product.parent_experience.price
            else:
                product.adults_price = product.parent_experience.price
                product.total_price = product._count_new_total_price()
            product.price_is_special = False
            product.save()

        # Apply discounts to subsequent products
        for i, product in enumerate(products):
            if i == 0:
                # Skip discount for the first product
                continue

            discount = product.parent_experience.second_purchase_discount
            if not discount:
                continue

            if product.parent_experience.is_private:
                new_total_price = product.total_price - discount
                product.total_price = max(new_total_price, Decimal('0.00'))  # Ensure price doesn't go negative
                product.stripe_price = int(product.total_price * 100)
            else:
                new_adult_price = product.adults_price - discount
                product.adults_price = max(new_adult_price, Decimal('0.00'))  # Ensure price doesn't go negative
                product.total_price = product._count_new_total_price()
                product.stripe_price = int(product.total_price * 100)

            product.price_is_special = True
            product.save()


@receiver(post_save, sender=Product)
def adjust_prices_after_update_status_expired(sender, instance, created, **kwargs):
    if created or instance.status != 'Expired':
        return

    session_key = instance.session_key

    if session_key:
        products = Product.pending.filter(session_key=session_key).order_by('created_at')

        # Reset discounts for all products
        for product in products:
            if product.parent_experience.is_private:
                product.total_price = product.parent_experience.price
            else:
                product.adults_price = product.parent_experience.price

            product.price_is_special = False
            product.save()

        # Apply discounts to subsequent products
        for i, product in enumerate(products):
            if i == 0:
                # Skip discount for the first product
                continue

            discount = product.parent_experience.second_purchase_discount
            if not discount:
                continue

            if product.parent_experience.is_private:
                new_total_price = product.total_price - discount
                product.total_price = max(new_total_price, Decimal('0.00'))  # Ensure price doesn't go negative
                product.stripe_price = int(product.total_price * 100)
            else:
                new_adult_price = product.adults_price - discount
                product.adults_price = max(new_adult_price, Decimal('0.00'))  # Ensure price doesn't go negative
                product.total_price = product._count_new_total_price()
                product.stripe_price = int(product.total_price * 100)

            product.price_is_special = True
            product.save()


@receiver(post_save, sender=Product)
def create_qrcode(sender, instance, created, **kwargs):
    if created:
        create_qrcode_for_product(instance)
