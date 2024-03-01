import logging
import json
import stripe

from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from products.models import Product
from products.views import UserIsAuthentiacedOrSessionKeyRequiredMixin
from purchases.models import Purchase
from service_layer.events import StripeSessionCompleted, StripeCustomerCreated
from service_layer.bus_messages import handle

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

BASE_ENDPOINT = settings.BASE_ENDPOINT


class BillingDetailView(UserIsAuthentiacedOrSessionKeyRequiredMixin, ListView):
    """View for listing all products for current user (session) only."""
    model = Product
    template_name = 'purchases/embedded_stripe_payment.html'
    queryset = Product.pending.all()
    extra_context = {'current_language': 'en'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_ids = [product.pk for product in self.queryset.all()]
        context['product_ids'] = product_ids
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context


@csrf_exempt
def checkout_view(request):
    if not request.method == "POST":
        return HttpResponseBadRequest()
    user = request.user
    try:
        data = json.loads(request.body.decode('utf-8'))
        product_ids = data.get('product_ids', [])
        product_ids = [int(pk) for pk in product_ids]
        products = Product.active.filter(id__in=product_ids)

        confirmation_path = reverse_lazy("confirmation", kwargs={'lang': 'en'}).lstrip('/')
        confirmation_url = f"{BASE_ENDPOINT}{confirmation_path}" + "?session_id={CHECKOUT_SESSION_ID}"

        session_data = dict(
            mode='payment',
            ui_mode='embedded',
            billing_address_collection='required',
            return_url=confirmation_url,
        )

        line_items = []
        total_amount = 0
        for product in products:
            total_amount += product.stripe_price
            item = {
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': product.stripe_product_id,
                    },
                    'unit_amount': product.stripe_price,
                },
                'quantity': 1,
            }
            line_items.append(item)

        session_data.update({'line_items': line_items})

        if user.is_authenticated:
            purchase = Purchase.objects.create(user=user, stripe_price=total_amount)
            session_data.update({"customer_creation": "if_required"})
        else:
            purchase = Purchase.objects.create(stripe_price=total_amount)
            session_data.update({"customer_creation": "always"})
        purchase.products.set(products)

        checkout_session = stripe.checkout.Session.create(**session_data)

        purchase.stripe_checkout_session_id = checkout_session.id
        purchase.save()

        return JsonResponse({'clientSecret': checkout_session.client_secret})
    except json.JSONDecodeError as exp:
        return HttpResponseBadRequest('Invalid JSON data')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
        logger.info(f"Received event: {event.id}.\n")
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Completed session: {session.id}")
        session_event = StripeSessionCompleted(session_id=session.id, payment_intent_id=session.payment_intent, customer_id=session.customer)
        handle(session_event)

    if event.type == 'checkout.session.expired':
        session = event['data']['object']
        logger.info(f"Expired session: {session.id}")

    if event.type == 'customer.created':
        customer = event['data']['object']
        logger.info(f"Customer created: {customer.id}")
        customer_event = StripeCustomerCreated(
            stripe_customer_id=customer['id'],
            name=customer['name'],
            email=customer['email'],
            phone=customer['phone'],
            address_city=customer['address']['city'],
            address_country=customer['address']['country'],
            address_line1=customer['address']['line1'],
            address_line2=customer['address']['line2'],
            address_postal_code=customer['address']['postal_code'],
            address_state=customer['address']['state']
        )
        handle(customer_event)
    else:
        logger.info('Unhandled event type {}'.format(event['type']))
    return HttpResponse(status=200)


class ConfirmationView(TemplateView):
    template_name = 'purchases/confirmation.html'
