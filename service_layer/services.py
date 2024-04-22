import logging
import time

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import User, Profile
from products.models import Product
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


def update_purchase_by_payment_intent_id(payment_intent_id: str, customer_id: str = None):
    try:
        # Update purchase status
        purchase = Purchase.objects.filter(stripe_payment_intent_id=payment_intent_id).first()
        purchase.completed = True
        purchase.save()
        if customer_id is not None:
            purchase.stripe_customer_id = customer_id
            purchase.save()
        logger.info(f"Completed payment for Purchase {purchase}\n")

        # Update Products statuses included in Purchase
        products = purchase.products.all()
        for product in products:
            product.status = "Payment"
            product.save()
            logger.info(f"Completed payment for {product}\n")
    except Exception as e:
        logger.error(f"Exception while handling payment: {e}")


def handle_charge_success(payment_intent_id: str, name: str, email: str, phone: str = '', address_city: str = '', address_country: str = '',
                          address_line1: str = '', address_line2: str = '', address_postal_code: str = '', address_state: str = '', **kwargs):
    logger.info(f"Handling charge success for payment intent: {payment_intent_id}.")
    # Check user exist
    if not User.objects.filter(email=email).exists():
        logger.info(f"Email address {email} does not exist.")
        # Create Stripe Customer
        customer = create_new_stripe_customer_id(name, email, phone, address_city, address_country, address_line1,
                                                 address_line2, address_postal_code, address_state)
        logger.info(f"Created customer {customer}")
        if customer.id:
            result = create_profile_and_generate_password(customer.id, name, email, phone, address_city, address_country, address_line1,
                                                 address_line2, address_postal_code, address_state)
            if result:
                set_real_user_in_purchase(payment_intent_id, customer.id)


def create_new_stripe_customer_id(name: str, email: str, phone: str = '', address_city: str = '', address_country: str = '', address_line1: str = '',
                                  address_line2: str = '', address_postal_code: str = '', address_state: str = ''):
    data = {
        'name': name,
        'email': email,
        'phone': phone,
        'address': {
            'city': address_city,
            'country': address_country,
            'line1': address_line1,
            'line2': address_line2,
            'postal_code': address_postal_code,
            'state': address_state
        }
    }
    customer = stripe.Customer.create(**data)
    return customer


def set_real_user_in_purchase(payment_intent_id: str, customer_id: str, max_attempts=3, retry_delay=5):
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

    purchases = Purchase.last24hours_manager.filter(stripe_payment_intent_id=payment_intent_id, user_id__in=[None, 0, 1])
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
                                         address_postal_code: str = None, address_state: str = None, **kwargs) -> bool:
    if email is None:
        return False
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
            return True

    except Exception as e:
        logger.error(f"Exception while handling customer: {e}")
        return False


def send_new_password_by_email(email: str, password: str, name: str = '',
                               subject: str = 'Your New Password',
                               template_name: str = 'email_templates/new_password_email.html',
                               from_email: str = None):
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    # Render the HTML template with the provided context
    html_message = render_to_string(template_name, {'password': password, 'name': name})

    # Send the email
    send_mail(subject=subject, message='', html_message=html_message,
              from_email=from_email, recipient_list=[email], fail_silently=False)
    logger.info(f"Email sent to {email}.")


# Product services

def send_product_created_email(product_id: int = None, product_name: str = None, product_start_date: str = None, product_start_time: str = None,
                               total_price: float = None, adult: int = None, children: int = None, product_type: str = None):
    subject = f'[{product_id}] New Product Created'
    message = (f'\tA new product "{product_name}" (ID: {product_id}) has been created.\n'
               f'Start: {product_start_date} {product_start_time}. Type: {product_type}.\n'
               f'Total: {total_price} EUR. Adult: {adult}. Children: {children}.')
    send_mail(subject, message, settings.SERVER_EMAIL, [settings.ADMIN_EMAIL])


def send_product_changed_email(product_id: int = None, product_name: str = None, product_start_date: str = None, product_start_time: str = None,
                               total_price: float = None, adult: int = None, children: int = None, product_type: str = None, status: str = None):
    subject = f'[{product_id}] Product Changed'
    message = (f'\tThe product "{product_name}" (ID: {product_id}) has been changed.\n'
               f'Start: {product_start_date} {product_start_time}. Type: {product_type}.\n'
               f'Total: {total_price} EUR. Adult: {adult}. Children: {children}.\n'
               f'Status: {status}.')
    send_mail(subject, message, settings.SERVER_EMAIL, [settings.ADMIN_EMAIL])


def update_products_status_if_expired():
    logger.info(f'Start updating status of expired products.')
    queryset = Product.objects.filter(status='Pending').all()
    logger.info(f'queryset length: {len(queryset)}')
    updated_products = []
    if queryset.count() > 0:
        now = timezone.now()
        for product in queryset:
            logger.info(f'Updating status of product "{product.stripe_product_id}"')
            if product.expired_time < now:
                logger.info(f'Product "[{product.id}]{product.stripe_product_id}" is expired.')
                product.status = 'Expired'
                product.save()
                updated_products.append(product)
                logger.info(f'Product ID={product.id} {product} has been updated. Its status is: {product.status}.')
    logger.info(f'Finish updating status of expired products.')
    return updated_products
