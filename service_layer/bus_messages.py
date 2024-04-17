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

def send_email_about_new_product(event: events.NewProductCreated):
    event_dict = event.__dict__
    services.send_product_created_email(**event_dict)


def send_email_about_changed_product(event: events.ProductUpdated):
    event_dict = event.__dict__
    services.send_product_changed_email(**event_dict)


# Stripe PaymentIntent

def set_purchase_status_completed(event: events.StripePaymentIntentSucceeded):
    event_dict = event.__dict__
    services.update_purchase_by_payment_intent_id(**event_dict)


# Main handlers dict

HANDLERS = {
    events.NewProductCreated: [send_email_about_new_product, ],
    events.ProductUpdated: [send_email_about_changed_product, ],
    events.StripePaymentIntentSucceeded: [set_purchase_status_completed, ],
    events.StripeChargeSucceeded: [handle_stripe_charge_success,]
}
