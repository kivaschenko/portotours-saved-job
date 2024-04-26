from dataclasses import dataclass


@dataclass
class Event:
    pass


@dataclass
class ProductPaid(Event):
    product_id: int
    customer_id: int
    product_name: str
    total_price: float


@dataclass
class ProductCancelled(ProductPaid):
    status: str


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
