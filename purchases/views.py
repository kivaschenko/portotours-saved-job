import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView
from django.db.models import Sum

from products.models import Product
from products.views import UserIsAuthentiacedOrSessionKeyRequiredMixin
from purchases.models import Purchase
from service_layer.bus_messages import handle
from service_layer.events import StripePaymentIntentSucceeded, StripePaymentIntentFailed, StripeChargeSucceeded, StripeCustomerCreated

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

        # Fetch all products
        products = self.get_queryset()

        # Calculate total sum of total_price for all products
        total_sum = products.aggregate(total_sum=Sum('total_price'))['total_sum']
        context['total_sum'] = total_sum if total_sum else 0

        # Other context data
        context['product_ids'] = [product.pk for product in products]
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return_path = reverse_lazy("payment-form", kwargs={'lang': 'en'})
        context['return_url'] = f'{BASE_ENDPOINT}{return_path}'

        return context


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

    if event.type == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        logger.info(f"Received payment intent: {payment_intent.id} failed.\n")
        error = payment_intent['last_payment_error']
        logger.error(f'A payment failed due to {error["message"]}.')
        billing_details = error['payment_method']['billing_details']
        handlers = []
        payment_intent_event = StripePaymentIntentFailed(
            payment_intent_id=payment_intent.id,
            stripe_customer_id=payment_intent.customer,
            error_code=error['code'],
            error_message=error['message'],
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
        handlers.append(payment_intent_event)
        for handler in handlers:
            handle(handler)

    if event.type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"PaymentIntent {payment_intent.id} succeeded.")
        handlers = []
        payment_intent_event = StripePaymentIntentSucceeded(payment_intent_id=payment_intent.id)
        handlers.append(payment_intent_event)
        for handler in handlers:
            handle(handler)

    if event.type == 'charge.succeeded':
        charge = event['data']['object']
        logger.info(f"Charge {charge.id} succeeded.")
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

    if event.type == 'customer.created':
        customer = event['data']['object']
        logger.info(f"Stripe customer {customer.id} created.")
        logger.info(f"Start creation of Profile {customer.id}.")
        stripe_customer_created_event = StripeCustomerCreated(
            stripe_customer_id=customer.id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address_city=customer['address']['city'],
            address_country=customer['address']['country'],
            address_line1=customer['address']['line1'],
            address_line2=customer['address']['line2'],
            address_postal_code=customer['address']['postal_code'],
            address_state=customer['address']['state']
        )
        handle(stripe_customer_created_event)

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
                "apple_pay",
                # "google_pay",
                "paypal",
                "klarna"
            ],
            "payment_method_options": {
                "card": {
                    "request_three_d_secure": "automatic"
                },
            },
            "metadata": {
                "product_ids": str(product_ids),
            }
        }
        customer_data = {
            'name': '',
            'email': '',
            'phone': '',
            'address': {
                'city': '',
                'country': '',
                'line1': '',
                'line2': '',
                'postal_code': '',
                'state': ''
            }
        }
        if user.is_authenticated:
            purchase = Purchase.objects.create(user=user, stripe_price=total_amount, stripe_customer_id=user.profile.stripe_customer_id)
            intent_data.update({'customer': user.profile.stripe_customer_id})  # Update customer directly as a string
            customer_data.update(
                {
                    'name': user.profile.name,
                    'email': user.profile.email,
                    'phone': user.profile.phone,
                    'address': {
                        'city': user.profile.address_city,
                        'country': user.profile.address_country,
                        'line1': user.profile.address_line1,
                        'line2': user.profile.address_line2,
                        'postal_code': user.profile.address_postal_code,
                        'state': user.profile.address_state
                    }
                }
            )
        else:
            purchase = Purchase.objects.create(stripe_price=total_amount)
        purchase.products.set(products)
        payment_intent = stripe.PaymentIntent.create(**intent_data)
        purchase.stripe_payment_intent_id = payment_intent.id
        purchase.save()
        return JsonResponse({'clientSecret': payment_intent.client_secret, 'customerData': customer_data, 'paymentAmount': payment_intent.amount})
    except json.JSONDecodeError as e:
        return HttpResponseBadRequest('Invalid JSON data')
