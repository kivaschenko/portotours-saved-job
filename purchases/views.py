import logging
import json

from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import stripe

from products.models import Product
from .models import Purchase
from service_layer.services import handle_successful_payment

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

BASE_ENDPOINT = settings.BASE_ENDPOINT


def billing_details(request):
    if not request.method == 'POST':
        return HttpResponseBadRequest()
    
    product_ids = request.POST.getlist('product_ids')
    product_ids = [int(pk) for pk in product_ids[0].strip().split(',')]

    context = {'product_ids': product_ids}

    stripe_public_key = settings.STRIPE_PUBLIC_KEY

    context.update({'stripe_public_key': stripe_public_key})

    return render(request, template_name='purchases/embedded_stripe_form.html', context=context)

    

@login_required(login_url='accounts/login/')
def checkout_view(request):
    if not request.method == "POST":
        return HttpResponseBadRequest()

    product_ids = request.POST.getlist('product_ids')
    product_ids = [int(pk) for pk in product_ids[0].strip().split(',')]
    products = Product.active.filter(id__in=product_ids)
    
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
        
    purchase = Purchase.objects.create(user=request.user, stripe_price=total_amount)
    purchase.products.set(products)
    request.session['purchase_id'] = purchase.id
    
    success_path = reverse("success").lstrip('/')
    cancel_path = reverse("stopped").lstrip('/')
    success_url = f"{BASE_ENDPOINT}{success_path}"
    cancel_url = f"{BASE_ENDPOINT}{cancel_path}"

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            ui_mode='inline',  # Change UI mode to inline
            billing_address_collection='required',
            success_url=success_url,
            cancel_url=cancel_url
        )
        purchase.stripe_checkout_session_id = checkout_session.id
        purchase.save()
        return JsonResponse({'sessionId': checkout_session.id})  # Send session ID back to frontend
    except stripe.error.CardError as e:
        print('payment_intent', e)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
        logger.info(f"Received event: {event}.\n")
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'checkout.session.completed':  # 'charge.succeeded'
        # Payment was successful
        handle_successful_payment(event)
    elif event['type'] == 'checkout.session.expired':
      session = event['data']['object']
    elif event['type'] == 'payment_intent.amount_capturable_updated':
      payment_intent = event['data']['object']
    elif event['type'] == 'payment_intent.canceled':
      payment_intent = event['data']['object']
    elif event['type'] == 'payment_intent.created':
      payment_intent = event['data']['object']
    elif event['type'] == 'payment_intent.partially_funded':
      payment_intent = event['data']['object']
    elif event['type'] == 'payment_intent.payment_failed':
      payment_intent = event['data']['object']
    elif event['type'] == 'payment_intent.processing':
      payment_intent = event['data']['object']
    elif event['type'] == 'payment_intent.requires_action':
      payment_intent = event['data']['object']
    elif event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
    # ... handle other event types
    else:
        logger.info('Unhandled event type {}'.format(event['type']))
    return HttpResponse(status=200)


def purchase_success_view(request):
    purchase_id = request.session.get("purchase_id")
    if purchase_id:
        purchase = Purchase.objects.get(id=purchase_id)
        purchase.completed = True
        purchase.save()
        del request.session['purchase_id']
        return HttpResponseRedirect(reverse('home'))
    return HttpResponse(f"Finished {purchase_id}")


def purchase_stopped_view(request):
    purchase_id = request.session.get("purchase_id")
    if purchase_id:
        purchase = Purchase.objects.get(id=purchase_id)
        products = purchase.products
        print(products)
        del request.session['purchase_id']
        return HttpResponseRedirect(reverse("home"))
    return HttpResponse("Stopped")