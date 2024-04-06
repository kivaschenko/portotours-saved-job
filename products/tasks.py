from celery import shared_task


@shared_task()
def add(x=2, y=3):
    z = x + y
    print(f"z={z}")


@shared_task()
def check_expired_products():
    from service_layer.services import update_products_status_if_expired
    update_products_status_if_expired()
