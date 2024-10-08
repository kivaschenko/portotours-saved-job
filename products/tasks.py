from celery import shared_task


@shared_task()
def check_expired_products():
    from service_layer.services import update_products_status_if_expired
    update_products_status_if_expired()


@shared_task()
def complete_charge_success(payment_intent_id: str, stripe_customer_id: str, name: str, email: str, phone: str = '', address_city: str = '',
                            address_country: str = '',
                            address_line1: str = '', address_line2: str = '', address_postal_code: str = '', address_state: str = '', **kwargs):
    from service_layer.services import handle_charge_success
    handle_charge_success(payment_intent_id, stripe_customer_id, name, email, phone, address_city, address_country, address_line1, address_line2,
                          address_postal_code,
                          address_state)


@shared_task()
def create_profile_and_send_password(stripe_customer_id: str = None, name: str = None, email: str = None, phone: str = None,
                                     address_city: str = None, address_country: str = None, address_line1: str = None, address_line2: str = None,
                                     address_postal_code: str = None, address_state: str = None, **kwargs):
    from service_layer.services import create_profile_and_generate_password
    create_profile_and_generate_password(stripe_customer_id, name, email, phone, address_city, address_country, address_line1, address_line2,
                                         address_postal_code, address_state, **kwargs)


@shared_task()
def report_about_paid():
    from service_layer.services import send_report_about_paid_products
    send_report_about_paid_products()
