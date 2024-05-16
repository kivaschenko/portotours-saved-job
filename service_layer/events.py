from dataclasses import dataclass


@dataclass
class Event:
    pass


@dataclass
class StripeChargeSucceeded(Event):
    payment_intent_id: str
    name: str
    email: str
    phone: str
    address_city: str
    address_country: str
    address_line1: str
    address_line2: str
    address_postal_code: str
    address_state: str


@dataclass
class StripePaymentIntentSucceeded(Event):
    payment_intent_id: str
    customer_id: str = None


@dataclass
class StripePaymentIntentFailed(Event):
    payment_intent_id: str
    stripe_customer_id: str
    error_code: str
    error_message: str
    name: str
    email: str
    phone: str
    address_city: str
    address_country: str
    address_line1: str
    address_line2: str
    address_postal_code: str
    address_state: str


@dataclass
class StripeCustomerCreated(Event):
    stripe_customer_id: str
    name: str
    email: str
    phone: str
    address_city: str
    address_country: str
    address_line1: str
    address_line2: str
    address_postal_code: str
    address_state: str
