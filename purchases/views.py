import logging
import json
import stripe

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView
from django.contrib.auth.decorators import login_required

from products.models import Product
from products.views import UserIsAuthenticatedOrSessionKeyRequiredMixin
from purchases.models import Purchase
from service_layer.events import StripeSessionCompleted, StripeCustomerCreated
from service_layer.bus_messages import handle

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

BASE_ENDPOINT = settings.BASE_ENDPOINT


class BillingDetailView(UserIsAuthenticatedOrSessionKeyRequiredMixin, ListView):
    """View for listing all products for current user (session) only."""
    model = Product
    template_name = 'purchases/checkout.html'
    queryset = Product.pending.all()
    extra_context = {'current_language': 'en'}

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

    def setup(self, request, *args, **kwargs):
        super(ConfirmationView, self).setup(request, *args, **kwargs)
        if session_id := request.GET.get('session_id'):
            self.kwargs['session_id'] = session_id

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        session_id = self.kwargs.get('session_id')  # Retrieve session_id from kwargs
        if session_id:
            # Check session status
            session = stripe.checkout.Session.retrieve(session_id)
            customer_email = session['customer_details']['email']
            kwargs['customer_email'] = customer_email
            if session.status == 'complete':
                # Get Purchase instance
                purchase = Purchase.last24hours_manager.get(stripe_checkout_session_id=session.id)
                object_list = purchase.products.all()
                kwargs.update({'purchase': purchase, 'status': 'complete', 'object_list': object_list})
            elif session.status == 'open':
                kwargs['status'] = 'open'
        return kwargs


@csrf_exempt
def checkout_payment_intent_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed")
    print("Start checkout.")
    print("request.method", request.method)
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

        intent_data = dict(
            currency='eur',
            amount=total_amount,
            automatic_payment_methods={"enabled": True},
        )

        if user.is_authenticated:
            purchase = Purchase.objects.create(user=user, stripe_price=total_amount, stripe_customer_id=user.profile.stripe_customer_id)
            intent_data.update({'customer': user.profile.stripe_customer_id})
        else:
            purchase = Purchase.objects.create(stripe_price=total_amount)
        purchase.products.set(products)

        payment_intent = stripe.PaymentIntent.create(**intent_data)

        purchase.stripe_payment_intent_id = payment_intent.id
        purchase.save()

        return JsonResponse({'clientSecret': payment_intent.client_secret})

    except json.JSONDecodeError as e:
        return HttpResponseBadRequest('Invalid JSON data')

