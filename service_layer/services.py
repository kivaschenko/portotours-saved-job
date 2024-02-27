import logging
import stripe
from django.conf import settings

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


def try_stripe_intent(amount, currency='eur'):
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
    )
    return intent
