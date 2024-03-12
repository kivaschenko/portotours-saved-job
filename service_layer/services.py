import logging
import stripe
import time

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from accounts.models import User, CustomUserManager, Profile
from purchases.models import Purchase

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
BASE_ENDPOINT = settings.BASE_ENDPOINT


# Purchase services

def update_purchase_by_stripe_session(session_id: str, payment_intent_id: str, customer_id: str):
    try:
        # Update purchase status
        purchase = Purchase.objects.get(stripe_checkout_session_id=session_id)
        purchase.completed = True
        purchase.stripe_payment_intent_id = payment_intent_id
        purchase.stripe_customer_id = customer_id
        purchase.save()
        logger.info(f"Completed payment for {purchase}\n")

        # Update Products statuses included in Purchase
        products = purchase.products.all()
        for product in products:
            product.status = "Payment"
            product.save()
            logger.info(f"Completed payment for {product}\n")
    except Exception as e:
        logger.error(f"Exception while handling payment: {e}")


def set_real_user_in_purchase(session_id: str, customer_id: str, max_attempts=3, retry_delay=5):
    attempt = 0

    while attempt < max_attempts:
        try:
            profile = Profile.objects.get(stripe_customer_id=customer_id)
            break  # If profile is successfully fetched, exit the loop
        except Profile.DoesNotExist:
            attempt += 1
            if attempt >= max_attempts:
                logger.error("Max attempts reached. Could not fetch profile.")
                return

            logger.warning(f"Profile not found. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    purchases = Purchase.last24hours_manager.filter(stripe_checkout_session_id=session_id, user_id__in=[None, 0, 1])
    if purchases:
        try:
            for purchase in purchases:
                if purchase.user_id == 1:  # no real user, admin assigned
                    purchase.user = profile.user
                    purchase.save()
                    # Update user in products
                    products = purchase.products.all()
                    for product in products:
                        product.customer = purchase.user
                        product.save()
                        logger.info(f"Updated user for {product}\n")

        except Exception as e:
            logger.error(f"Exception while handling purchase: {e}")


# Profile services

def get_first_last_name(customer_name):
    first_name = last_name = ''
    try:
        split_name = customer_name.split(' ')
        if len(split_name) > 1:
            first_name, *_, last_name = split_name
        else:
            first_name = customer_name
    except Exception as e:
        logger.error(f"Exception while handling customer name: {e}")
    finally:
        return first_name, last_name


def create_profile_and_generate_password(stripe_customer_id: str = None, name: str = None, email: str = None, phone: str = None,
                                         address_city: str = None, address_country: str = None, address_line1: str = None, address_line2: str = None,
                                         address_postal_code: str = None, address_state: str = None, **kwargs) -> None:
    if email is None:
        return
    try:
        if not User.objects.filter(username=email).exists():
            if name is not None:
                first_name, last_name = get_first_last_name(name)
            else:
                first_name, last_name = None, None
            # Create a new user
            new_user, new_password = User.objects.create_user_without_password(email, first_name=first_name, last_name=last_name)
            logger.info(f"New user: {new_user}\n")

            profile = Profile(user=new_user, stripe_customer_id=stripe_customer_id, name=name, email=email, phone=phone, address_city=address_city,
                              address_country=address_country, address_line1=address_line1, address_line2=address_line2,
                              address_postal_code=address_postal_code,
                              address_state=address_state)
            profile.save()
            logger.info(f'Profile created with id: {profile.id}')
            send_new_password_by_email(profile.email, new_password, profile.name)

    except Exception as e:
        logger.error(f"Exception while handling customer: {e}")


def send_new_password_by_email(email: str, password: str, name: str = '',
                               subject: str = 'Your New Password',
                               template_name: str = 'email_templates/new_password_email.html',
                               from_email: str = 'One Day Tours <info@onedaytours.com>'):
    # Render the HTML template with the provided context
    html_message = render_to_string(template_name, {'password': password, 'name': name})

    # Send the email
    send_mail(subject=subject, message='', html_message=html_message,
              from_email=from_email, recipient_list=[email], fail_silently=False)


# Product services

def create_new_product():
    pass

def update_event_for_product(event_id: str):
    pass

def create_occurence_for_product(event_id: int):
    pass