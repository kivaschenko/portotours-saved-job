import logging
import stripe

from django.core.mail import send_mail
from django.conf import settings

from accounts.models import User, CustomUserManager, Profile
from purchases.models import Purchase

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
BASE_ENDPOINT = settings.BASE_ENDPOINT


def handle_successful_payment(event):
    try:
        # Update purchase status
        session = event.data.object
        purchase = Purchase.objects.get(stripe_checkout_session_id=session.id)
        purchase.completed = True
        purchase.stripe_payment_intent_id = session.payment_intent
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


def handle_customer_created(event):
    try:
        customer = event.data.object
        print('New customer created', customer)
        email = customer.email
        # Check if user exists based on the received data
        if not User.objects.filter(username=email).exists():
            if customer.name:
                first_name, last_name = get_first_last_name(customer.name)
            else:
                first_name, last_name = None, None
            # Create a new user
            new_user, new_password = User.objects.create_user_without_password(email, first_name=first_name, last_name=last_name)
            # Send password to the user by email
            send_mail(
                'Your New Password',
                f'Your new password is: {new_password}',
                settings.EMAIL_HOST_USER,
                [new_user.email],
                fail_silently=False,
            )
        # extract data
        data = dict(
            stripe_customer_id=customer.id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address_city=customer.address.city,
            address_country=customer.address.country,
            address_line1=customer.address.line1,
            address_line2=customer.address.line2,
            address_postal_code=customer.address.postal_code,
            address_state=customer.address.state,
        )
        profile, created = Profile(user=new_user, email=email)
        profile.save()
        print(f'Created Profile {profile}')
    except Exception as e:
        logger.error(f"Exception while handling customer: {e}")


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
