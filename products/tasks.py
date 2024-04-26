from celery import shared_task


@shared_task()
def add(x=2, y=3):
    z = x + y
    print(f"z={z}")


@shared_task()
def check_expired_products():
    from service_layer.services import update_products_status_if_expired
    update_products_status_if_expired()


@shared_task()
def complete_charge_success(payment_intent_id: str, name: str, email: str, phone: str = '', address_city: str = '', address_country: str = '',
                            address_line1: str = '', address_line2: str = '', address_postal_code: str = '', address_state: str = '', **kwargs):
    from service_layer.services import handle_charge_success
    handle_charge_success(payment_intent_id, name, email, phone, address_city, address_country, address_line1, address_line2, address_postal_code,
                          address_state)

@shared_task()
def send_notifications_about_paid_products(payment_intent_id: str):
    pass