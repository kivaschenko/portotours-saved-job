from decimal import Decimal
from dataclasses import dataclass


@dataclass
class Event:
    pass


@dataclass
class NewProductCreated(Event):
    total_price: Decimal
    product_id: int
    product_name: str
    product_start_date: str
    product_start_time: str
    adult: int
    children: int


@dataclass
class ProductStatusUpdated(NewProductCreated):
    status: str

