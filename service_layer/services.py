import logging
import time

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import User, Profile
from products.models import Product
from products.product_services import update_experience_event_booking
from purchases.models import Purchase

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
BASE_ENDPOINT = settings.BASE_ENDPOINT


# Purchase services


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
    logger.info(f'Creating Stripe customer {customer}.\n')
    return customer


def set_real_user_in_purchase(payment_intent_id: str, customer_id: str, max_attempts=5, retry_delay=5):
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
        if name is not None:
            first_name, last_name = get_first_last_name(name)
        else:
            first_name, last_name = None, None
        # Create a new user
        new_user, new_password, created = User.objects.get_or_create_user(email, first_name=first_name, last_name=last_name)
        if created:
            logger.info(f"New user: {new_user} created with a new password.\n")
            profile = Profile(user=new_user, stripe_customer_id=stripe_customer_id, name=name, email=email, phone=phone, address_city=address_city,
                              address_country=address_country, address_line1=address_line1, address_line2=address_line2,
                              address_postal_code=address_postal_code,
                              address_state=address_state)
            profile.save()
            logger.info(f'Profile created with id: {profile.id}')
        else:
            logger.info(f"New user: {new_user} updated with a new password.\n")
        send_new_password_by_email(email, new_password, new_user)
    except Exception as e:
        logger.error(f"Exception while handling customer: {e}")


def send_new_password_by_email(email: str, password: str, name: str = '',
                               subject: str = 'Your New Password',
                               template_name: str = 'email_templates/new_password_email.html',
                               from_email: str = None):
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    html_message = render_to_string(template_name, {'password': password, 'name': name})
    logger.info(f'Sending email to {email} to {name}.\n')
    send_mail(subject=subject, message='', html_message=html_message,
              from_email=from_email, recipient_list=[email], fail_silently=False)
    logger.info(f"New password sent to {email}.")


# ---------------------------
# Product & Purchase services

def send_product_paid_email_staff(product):
    subject = f'New Order: {product.random_order_number}, {product.full_name}, {product.date_of_start}'
    message = (f'\tProduct name: {product.full_name}\n'
               f'\tNumber of passengers: {product.total_booked}\n'
               f'\tLanguage: {product.language}\n'
               f'\tPassenger details: ({product.customer.profile.name}, {product.customer.profile.email}, {product.customer.profile.phone})\n')
    # send_mail(subject, message, from_email=settings.ORDER_EMAIL, recipient_list=[settings.ADMIN_EMAIL, settings.MANAGER_EMAIL],
    #           fail_silently=False)
    body = [message,]
    if product.number_added_options > 0:
        body.append(f'\tOptional extras included:\n')
        for option in product.options.filter(quantity__gt=0):
            option = f'\t\t{option.experience_option.name} {option.experience_option.description} x {option.quantity}\n'
            body.append(option)

    send_mail(subject=subject, message='\n'.join(body), from_email=settings.ORDER_EMAIL, recipient_list=[settings.ADMIN_EMAIL, settings.MANAGER_EMAIL],
              fail_silently=False)


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


def set_booking_after_payment(product):
    logger.info(f'Start setting booking after Product id: {product}.')
    total_booked = product.total_booked
    update_result = update_experience_event_booking(product.occurrence.event_id, booked_number=total_booked)
    if not update_result:
        status = f'Failed to update booking after ExperienceEvent id: {product.occurrence.event_id}.'
        logger.error(status)
    else:
        status = f'Succeeded setting booking after Product id: {product.id}.'
        logger.info(status)


def send_email_notification_to_customer(product):
    url = 'https://onedaytours.pt/en/generate-pdf/{}/'.format(product.id)
    subject = f'[{product.random_order_number}] Product paid'
    message = (f'Congratulations, {product.customer.profile.name}! \n\tYour product "{product.full_name}" (ID: {product.random_order_number}) paid.\n'
               f'Total price: {product.total_price} EUR.\n'
               f'You can download your PDF here: {url}.')
    # send_mail(subject, message, from_email=settings.ORDER_EMAIL, recipient_list=[product.customer.profile.email], fail_silently=False)
    message = (f'Congratulations, {product.customer.profile.name}!\n'
               f'\tYour product "{product.full_name}" (ID: {product.random_order_number}) paid.\n'
               f'\tTotal price: {product.total_price} EUR.\n')
    body = [message,]
    if product.number_added_options > 0:
        body.append(f'Optional extras included:\n')
        for option in product.options.filter(quantity__gt=0):
            option = f'\t\t{option.experience_option.name} {option.experience_option.description} x {option.quantity}\n'
            body.append(option)
    pdf_link = f'You can download your PDF here: {url}.'
    body.append(pdf_link)
    send_mail(subject=subject, message='\n'.join(body), from_email=settings.ORDER_EMAIL, recipient_list=[product.customer.profile.email], fail_silently=False)


def send_report_about_paid_products():
    products = Product.for_report.all()
    for product in products:
        set_booking_after_payment(product)
        send_product_paid_email_staff(product)
        send_email_notification_to_customer(product)
        product.reported = True
        product.save()


def update_purchase_and_send_email_payment_intent_failed(payment_intent_id: str = None, stripe_customer_id: str = '',
                                                         error_code: str = '', error_message: str = '',
                                                         name: str = '', email: str = '', phone: str = '', address_city: str = '',
                                                         address_country: str = '', address_line1: str = '', address_line2: str = '',
                                                         address_postal_code: str = '', address_state: str = ''):
    if payment_intent_id is None:
        logger.error('Inside function "service_layer.services.update_purchase_and_send_email_payment_intent_failed" payment_intent_id is empty.')
        return

    email_data = dict(
        subject=f'New Order payment failed: {payment_intent_id}, {error_code}',
        message=error_message,
        from_email=settings.ORDER_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL, settings.MANAGER_EMAIL],
    )

    try:
        logger.info(f'Start updating purchase and send email about PaymentIntent failed: {payment_intent_id}.')
        purchase = Purchase.objects.get(stripe_payment_intent_id=payment_intent_id)

        if stripe_customer_id and not purchase.stripe_customer_id:
            purchase.stripe_customer_id = stripe_customer_id

        purchase.error_code = error_code
        purchase.error_message = error_message
        purchase.save()

        subject, product_info = create_message_about_products(purchase)
        if subject and product_info:
            email_data['subject'] = subject
            email_data['message'] = product_info
    except Purchase.DoesNotExist:
        logger.error(f'Purchase {payment_intent_id} does not exist.')
    finally:
        client_info = (f"\nClient info:\n"
                       f"\tStripe ID: {stripe_customer_id}\n"
                       f"\tName: {name}\n"
                       f"\tEmail: {email}\n"
                       f"\tPhone: {phone}\n")
        error_info = (f"\nError info:\n"
                      f"\tError code: {error_code}\n"
                      f"\tError message: {error_message}\n")

        body = [email_data.get('message', ''), client_info, error_info]
        email_data['message'] = '\n'.join(body)

        send_mail(**email_data)


def create_message_about_products(purchase: Purchase):
    products = purchase.products.all()
    if not products:
        return None, None

    product_order_numbers = [product.random_order_number for product in products]
    subject = "Unsuccessful attempt of payment for order(s): " + ', '.join(product_order_numbers)
    purchase_info = f"Purchase Id: {purchase.id}\n"
    body = [purchase_info,]
    for product in products:
        message = (f"\nOrder ID: {product.random_order_number}\n"
                   f"\tProduct name: {product.full_name}\n"
                   f"\tNumber of passengers: {product.total_booked}\n"
                   f"\tLanguage: {product.language}\n"
                   f"\tTotal sum: €{product.total_price}\n")
        body.append(message)

    return subject, '\n'.join(body)
