from typing import Type

from service_layer import events, services
from products import tasks

base_event = Type[events.Event]


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


# Stripe Charge

def handle_stripe_charge_success(event: events.StripeChargeSucceeded):
    event_dict = event.__dict__
    tasks.complete_charge_success(**event_dict)


# Products

def send_email_about_new_product(event: events.ProductPaid):
    event_dict = event.__dict__
    tasks.send_notifications_about_paid_products.delay(**event_dict)


def update_booking_data_for_paid_product(event: events.ProductPaid):
    tasks.update_booking_data_for_product.delay(event.product_id)


# Stripe PaymentIntent

def set_purchase_status_completed(event: events.StripePaymentIntentSucceeded):
    event_dict = event.__dict__
    services.update_purchase_by_payment_intent_id(**event_dict)


# Main handlers dict

HANDLERS = {
    events.ProductPaid: [update_booking_data_for_paid_product, send_email_about_new_product],
    events.StripePaymentIntentSucceeded: [set_purchase_status_completed, ],
    events.StripeChargeSucceeded: [handle_stripe_charge_success, ]
}
