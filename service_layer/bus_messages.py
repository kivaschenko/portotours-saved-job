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
    new_password = services.create_profile_and_generate_password(**event_dict)

    # pass new password as attribute to next step to send by email
    event.password = new_password


def send_new_password(event: events.StripeCustomerCreated):
    services.send_new_password_by_email(event.email, event.password)


# Main handlers dict

HANDLERS = {
    events.StripeSessionCompleted: [
        update_purchase_status,
        update_purchase_customer,
    ],
    events.StripeCustomerCreated: [
        create_new_profile,
        send_new_password,
    ]
}
