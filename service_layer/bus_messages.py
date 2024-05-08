from typing import Type

from products import tasks
from service_layer import events, services

base_event = Type[events.Event]


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


# Stripe Charge

def handle_stripe_charge_success(event: events.StripeChargeSucceeded):
    event_dict = event.__dict__
    tasks.complete_charge_success(**event_dict)


# Stripe PaymentIntent

def set_purchase_status_completed(event: events.StripePaymentIntentSucceeded):
    event_dict = event.__dict__
    services.update_purchase_by_payment_intent_id(**event_dict)


# Stripe Customer

def check_profile_and_send_password_email(event: events.StripeCustomerCreated):
    event_dict = event.__dict__
    tasks.create_profile_and_send_password.delay(**event_dict)


# Main handlers dict

HANDLERS = {
    events.StripePaymentIntentSucceeded: [set_purchase_status_completed, ],
    events.StripeChargeSucceeded: [handle_stripe_charge_success, ],
    events.StripeCustomerCreated: [check_profile_and_send_password_email, ]
}
