import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from products.models import Product
from products.views import UserIsAuthentiacedOrSessionKeyRequiredMixin
from purchases.models import Purchase
from service_layer.bus_messages import handle
from service_layer.events import StripePaymentIntentSucceeded, StripeChargeSucceeded

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

BASE_ENDPOINT = settings.BASE_ENDPOINT


class BillingDetailView(UserIsAuthentiacedOrSessionKeyRequiredMixin, ListView):
    """View for listing all products for current user (session) only."""
    model = Product
    template_name = 'purchases/checkout.html'
    extra_context = {'current_language': 'en'}

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_ids = [product.pk for product in self.queryset.all()]
        context['product_ids'] = product_ids
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return_path = reverse_lazy("payment-form", kwargs={'lang': 'en'})
        context['return_url'] = f'{BASE_ENDPOINT}{return_path}'

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

        confirmation_path = reverse_lazy("confirmation", kwargs={'lang': 'en'})
        confirmation_url = f"{BASE_ENDPOINT}{confirmation_path}" + "?session_id={CHECKOUT_SESSION_ID}"

        session_data = dict(
            mode='payment',
            ui_mode='embedded',
            billing_address_collection='auto',
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
            purchase = Purchase.objects.create(user=user, stripe_price=total_amount, stripe_customer_id=user.profile.stripe_customer_id)
            session_data.update({'customer': user.profile.stripe_customer_id})
        else:
            purchase = Purchase.objects.create(stripe_price=total_amount)
            # if new anonymous user, then create a new Stripe customer with billing address
            session_data.update({"customer_creation": "always"})
            session_data.update({"billing_address_collection": 'required'})
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

    if event.type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"PaymentIntent {payment_intent.id} succeeded.")
        payment_intent_event = StripePaymentIntentSucceeded(payment_intent_id=payment_intent.id)
        handle(payment_intent_event)

    if event.type == 'charge.succeeded':
        charge = event['data']['object']
        logger.info(f"Charge {charge.id} succeeded.")
        print(charge)
        billing_details = charge.billing_details

        charge_event = StripeChargeSucceeded(
            payment_intent_id=charge.payment_intent,
            name=billing_details.name,
            email=billing_details.email,
            phone=billing_details.phone,
            address_city=billing_details['address']['city'],
            address_country=billing_details['address']['country'],
            address_line1=billing_details['address']['line1'],
            address_line2=billing_details['address']['line2'],
            address_postal_code=billing_details['address']['postal_code'],
            address_state=billing_details['address']['state']
        )
        handle(charge_event)

    else:
        logger.info('Unhandled event type {}'.format(event['type']))
    return HttpResponse(status=200)


class ConfirmationView(TemplateView):
    template_name = 'purchases/confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_intent_id = self.request.GET.get('payment_intent_id')
        if payment_intent_id:
            purchase = Purchase.last24hours_manager.filter(stripe_payment_intent_id=payment_intent_id).first()
            if purchase:
                object_list = purchase.products.all()
                context.update({'purchase': purchase, 'object_list': object_list})
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.request.GET.get('payment_intent_id'):
            redirect_url = reverse_lazy('payment-form', kwargs={'lang': 'en'})
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)


@csrf_exempt
def checkout_payment_intent_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed")
    print("request.body", request.body)
    user = request.user
    try:
        data = json.loads(request.body.decode('utf-8'))
        product_ids = data.get('product_ids', [])
        product_ids = [int(pk) for pk in product_ids]
        products = Product.active.filter(id__in=product_ids)

        total_amount = 0
        for product in products:
            total_amount += product.stripe_price

        intent_data = {
            "amount": total_amount,
            "currency": "eur",
            "payment_method_types": [
                "card",
                # "apple_pay",
                # "google_pay",
                "paypal",
                "klarna"
            ],
            "payment_method_options": {
                "card": {
                    "request_three_d_secure": "automatic"
                },
                # "apple_pay": {
                #     # Apple Pay specific options if needed
                # },
                # "google_pay": {
                #     # Google Pay specific options if needed
                # },
                "paypal": {
                    # PayPal specific options if needed
                },
                "klarna": {
                    # Klarna specific options if needed
                }
            },
            "metadata": {
                "product_ids": str(product_ids),
            }
        }
        if user.is_authenticated:
            purchase = Purchase.objects.create(user=user, stripe_price=total_amount, stripe_customer_id=user.profile.stripe_customer_id)
            intent_data.update({'customer': {'id': user.profile.stripe_customer_id}})
        else:
            purchase = Purchase.objects.create(stripe_price=total_amount)
        purchase.products.set(products)

        payment_intent = stripe.PaymentIntent.create(**intent_data)

        purchase.stripe_payment_intent_id = payment_intent.id
        purchase.save()

        return JsonResponse({'clientSecret': payment_intent.client_secret})

    except json.JSONDecodeError as e:
        return HttpResponseBadRequest('Invalid JSON data')
