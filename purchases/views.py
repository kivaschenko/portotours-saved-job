import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView
from django.db.models import Sum

from products.models import Product
from products.views import UserIsAuthenticatedOrSessionKeyRequiredMixin
from products.product_services import prepare_google_items_for_cart
from purchases.models import Purchase
from service_layer.bus_messages import handle
from service_layer.events import StripePaymentIntentSucceeded, StripePaymentIntentFailed, StripeChargeSucceeded, StripeCustomerCreated

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

BASE_ENDPOINT = settings.BASE_ENDPOINT


class BillingDetailView(UserIsAuthenticatedOrSessionKeyRequiredMixin, ListView):
    model = Product
    template_name = 'purchases/checkout.html'
    extra_context = {'current_language': 'en'}

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()
        total_sum = products.aggregate(total_sum=Sum('total_price'))['total_sum']
        if total_sum is None:
            total_sum = 0
        options_sum = products.aggregate(options_sum=Sum('options__total_sum'))['options_sum']
        if options_sum is None:
            options_sum = 0
        total_sum += options_sum
        context['total_sum'] = total_sum if total_sum else 0
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
        logger.info(f"Received event: {event.id}.")
    except ValueError:
        return HttpResponse(status=400)

    event_type_handlers = {
        'payment_intent.payment_failed': handle_payment_intent_failed,
        # 'payment_intent.succeeded': handle_payment_intent_succeeded,
        # 'payment_intent.updated': payment_intent_updated,
        'charge.succeeded': handle_charge_succeeded,
        'customer.created': handle_customer_created
    }

    handler = event_type_handlers.get(event.type, handle_unhandled_event)
    handler(event)

    return HttpResponse(status=200)


def handle_payment_intent_failed(event):
    payment_intent = event['data']['object']
    logger.info(f"Received payment intent: {payment_intent.id} failed.")
    logger.info(f"Received payment intent:\n {payment_intent}")
    error = payment_intent['last_payment_error']
    logger.error(f'A payment failed due to {error["message"]}.')
    billing_details = error['payment_method']['billing_details']
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
    handle(payment_intent_event)


def handle_payment_intent_succeeded(event):
    payment_intent = event['data']['object']
    logger.info(f"PaymentIntent {payment_intent.id} succeeded.")
    logger.info(f"Received payment intent:\n {payment_intent}")
    payment_intent_event = StripePaymentIntentSucceeded(payment_intent_id=payment_intent.id)
    handle(payment_intent_event)


def handle_charge_succeeded(event):
    charge = event['data']['object']
    logger.info(f"Charge {charge.id} succeeded.")
    logger.info(f"Charge:\n {charge}")
    billing_details = charge.billing_details
    charge_event = StripeChargeSucceeded(
        payment_intent_id=charge.payment_intent,
        stripe_customer_id=charge.customer,
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


def handle_customer_created(event):
    customer = event['data']['object']
    logger.info(f"Stripe customer {customer.id} created.")
    logger.info(f"Stripe customer:\n {customer}")
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


def payment_intent_updated(event):
    payment_intent = event['data']['object']
    logger.info(f"Payment intent {payment_intent.id} updated.")
    logger.info(f"Received payment intent:\n {payment_intent}")
    payment_intent_event = StripePaymentIntentSucceeded(payment_intent_id=payment_intent.id)
    handle(payment_intent_event)


def handle_unhandled_event(event):
    logger.info(f'Unhandled event type {event.type}')


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
                context.update({'ecommerce_items': prepare_google_items_for_cart(object_list)})
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

        total_amount = sum(product.stripe_price for product in products)
        total_options_amount = sum(product.options_stripe_price for product in products)
        if total_options_amount:
            total_amount += total_options_amount
        payment_method_types = [
            "card",
            # "apple_pay",
            # "google_pay",
            # "paypal",
            "klarna",
        ]
        intent_data = {
            "amount": total_amount,
            "currency": "eur",
            "payment_method_types": payment_method_types,
            "payment_method_options": {
                "card": {
                    "request_three_d_secure": "automatic"
                },
                # "apple_pay": {},
                # "google_pay": {},
                # "paypal": {},
                "klarna": {}
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
            intent_data.update({'customer': user.profile.stripe_customer_id})
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
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON data')
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Stripe error: {e.user_message}")
        return HttpResponseBadRequest(f"Stripe error: {e.user_message}")
