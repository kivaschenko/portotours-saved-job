import logging
from decimal import Decimal

from celery import shared_task

logger = logging.Logger(__name__)


@shared_task()
def add(x=2, y=3):
    z = x + y
    print(f"z={z}")


@shared_task()
def send_new_password(email: str, password: str, name: str) -> None:
    from service_layer.services import send_new_password_by_email
    send_new_password_by_email(email, password, name)
