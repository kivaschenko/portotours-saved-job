import stripe
from django.http import HttpResponse, JsonResponse
import json
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings

from products.models import Product
from .models import Purchase
from .forms import ProductCartForm
from .services import handle_successful_payment

stripe.api_key = settings.STRIPE_SECRET_KEY

BASE_ENDPOINT = settings.BASE_ENDPOINT


@login_required(login_url='accounts/login/')
def checkout_view(request):
    if not request.method == "POST":
        return HttpResponseBadRequest()
    # get active products TODO: override this urgently!
    product_ids = request.POST.getlist('product_ids')
    product_ids = [int(id) for id in product_ids[0].strip().split(',')]
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
        # intent = stripe.PaymentIntent.create(
        #     amount=purchase.stripe_price,
        #     currency='eur',
        #     description=f'Purchase of products: Purchase.id:{purchase.id}',
        # )
        # print('intent', intent)
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            # ui_mode='embedded',
            ui_mode='hosted',
            success_url=success_url,
            cancel_url=cancel_url
        )
        purchase.stripe_checkout_session_id = checkout_session.id
        purchase.save()
        return HttpResponseRedirect(checkout_session.url)
    except stripe.error.CardError as e:
        print('payment_intent', e)

    # context = {
    #     'client_secret': session.client_secret,
    #     'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    # }
    # return JsonResponse(context)


def stripe_webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'checkout.session.completed':
        # Payment was successful
        handle_successful_payment(event)

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