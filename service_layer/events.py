from dataclasses import dataclass


@dataclass
class Event:
    pass


@dataclass
class NewProductCreated(Event):
    product_id: int
    product_name: str
    product_start_date: str
    product_start_time: str
    total_price: float
    adult: int
    children: int
    product_type: str


@dataclass
class ProductUpdated(NewProductCreated):
    status: str


@dataclass
class StripeSessionCompleted(Event):
    session_id: str
    payment_intent_id: str
    customer_id: str


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


@dataclass
class StripePaymentIntentSucceeded(Event):
    payment_intent_id: str
    customer_id: str = None
