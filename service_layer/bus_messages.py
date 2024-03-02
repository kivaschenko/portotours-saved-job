from typing import Type

from service_layer import events, services

base_event = Type[events.Event]


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


# Stripe Session

def update_purchase_status(event: events.StripeSessionCompleted):
    services.update_purchase_by_stripe_session(event.session_id, event.payment_intent_id, event.customer_id)
    # TODO: later will be exchanged by Celery task


def update_purchase_customer(event: events.StripeSessionCompleted):
    services.set_real_user_in_purchase(event.session_id, event.customer_id)
    # TODO: later will be exchanged by Celery task


# Stripe Customer

def create_new_profile(event: events.StripeCustomerCreated):
    # Convert the dataclass instance to a dictionary
    event_dict = event.__dict__
    # handle event data
    services.create_profile_and_generate_password(**event_dict)




# Main handlers dict

HANDLERS = {
    events.StripeSessionCompleted: [
        update_purchase_status,
        update_purchase_customer,
    ],
    events.StripeCustomerCreated: [
        create_new_profile,
    ]
}
