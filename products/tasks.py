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
def send_notifications_about_paid_products(product_id: int = None, product_name: str = None, total_price: float = None):
    from service_layer.services import send_product_paid_email_staff, send_product_paid_email_to_customer
    send_product_paid_email_staff(product_id, product_name, total_price)
    send_product_paid_email_to_customer(product_id, product_name, total_price)


@shared_task()
def update_booking_data_for_product(product_id: int = None):
    from service_layer.services import set_booking_after_payment
    set_booking_after_payment(product_id)
