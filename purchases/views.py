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


@login_required
def generate_purchase_pdf(request, purchase_id):
    # Retrieve the purchase object
    purchase = Purchase.objects.get(pk=purchase_id)

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="purchase_{purchase_id}.pdf"'

    # Create a canvas object
    c = canvas.Canvas(response, pagesize=letter)

    # Set up the initial position for drawing
    y_position = 750

    # Add logo image
    logo_path = 'static/images/attraction-img1.png'
    c.drawImage(logo_path, 100, 750, width=100, height=100)

    # Draw the product table
    data = [['Product Name', 'Adult', 'Children', 'Date | Time', 'Price']]
    for product in purchase.products.all():
        data.append([product.parent_experience, f"{product.adults_count} x {product.adults_price} EUR", f"{product.child_count} x {product.child_price}", f"{product.date_of_start} | {product.time_of_start}", f"{product.total_price} EUR"])

    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    table.wrapOn(c, 100, 600)
    table.drawOn(c, 100, 600)

    c.showPage()
    c.save()

    return response

