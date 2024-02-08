import stripe
from django.http import HttpResponse
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


def purchase_start_view(request):
    if not request.method == "POST":
        return HttpResponseBadRequest()
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    handle = request.POST.get("handle")
    obj = Product.objects.get(handle=handle)
    stripe_price_id = obj.stripe_price_id
    if stripe_price_id is None:
        return HttpResponseBadRequest()
    purchase = Purchase.objects.create(user=request.user, product=obj)
    request.session['purchase_id'] = purchase.id
    success_path = reverse("purchases:success")
    if not success_path.startswith("/"):
        success_path = f"/{success_path}"
    cancel_path = reverse("purchases:stopped")
    success_url = f"{BASE_ENDPOINT}{success_path}"
    cancel_url = f"{BASE_ENDPOINT}{cancel_path}"
    print(success_url, cancel_url)
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": stripe_price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url
    )
    purchase.stripe_checkout_session_id = checkout_session.id
    purchase.save()
    return HttpResponseRedirect(checkout_session.url)


def purchase_success_view(request):
    purchase_id = request.session.get("purchase_id")
    if purchase_id:
        purchase = Purchase.objects.get(id=purchase_id)
        purchase.completed = True
        purchase.save()
        del request.session['purchase_id']
        return HttpResponseRedirect(purchase.product.get_absolute_url())
    return HttpResponse(f"Finished {purchase_id}")


def purchase_stopped_view(request):
    purchase_id = request.session.get("purchase_id")
    if purchase_id:
        purchase = Purchase.objects.get(id=purchase_id)
        product = purchase.product
        del request.session['purchase_id']
        return HttpResponseRedirect(product.get_absolute_url())
    return HttpResponse("Stopped")


# Sample by stripe.Charge

@login_required
def checkout(request):
    if request.method == 'POST':
        form = ProductCartForm(request=request, data=request.POST)
        if form.is_valid():
            # Retrieve list of products
            product_list = request.POST.getlist('my_products')
            print(product_list)

        try:
            new_purchases = []
            total_amount = 0
            for product_id in product_list:
                product = Product.objects.get(pk=product_id)
                total_amount += product.stripe_price
                new_purchase = Purchase.objects.create(user=request.user, product=product)
                new_purchases.append(new_purchase)

            payment_intent = stripe.PaymentIntent.create(
                amount=total_amount,
                currency='eur',
                description='Purchase of products',
                source=token,
            )
            # do something with response from stripe API
            print('payment_intent', payment_intent)
        except stripe.error.CardError as e:
            return render(request, 'purchases/payment_error.html', {'error_message': e.error.message})
        else:
            return render(request, 'purchases/payment_success.html')
    else:
        form = ProductCartForm(user_id=request.user.id)

    return render(request, 'purchases/checkout.html', {'form': form})


@login_required(login_url='accounts/login/')
def checkout_payment_for_product_list(request):
    if not request.method == 'POST':
        return HttpResponseBadRequest()
    products = request.POST.getlist('my_products')
    products = [int(product_id) for product_id in products]
    products = Product.objects.filter(id__in=products, customer=request.user).all()
    total_amount = 0
    for product in products:
        total_amount += product.stripe_price
    purchase = Purchase.objects.create(user=request.user, stripe_price=total_amount)
    purchase.products.set(products)

    try:
        payment_intent_json = stripe.PaymentIntent.create(
            amount=purchase.stripe_price,
            currency='eur',
            description=f'Purchase of products: Purchase.id:{purchase.id}',
        )
        print('payment_intent_json', payment_intent_json)
        payment_intent = json.loads(payment_intent_json)
        success_path = reverse("purchases:success")
        if not success_path.startswith("/"):
            success_path = f"/{success_path}"
        cancel_path = reverse("purchases:stopped")
        success_url = f"{BASE_ENDPOINT}{success_path}"
        cancel_url = f"{BASE_ENDPOINT}{cancel_path}"
        print(success_url, cancel_url)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": payment_intent['amount'],
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url
        )
    except stripe.error.CardError as e:
        print('payment_intent', e)
        return render(request, 'purchases/payment_error.html', {'error_message': e.error.message})
    else:
        return render(request, 'purchases/payment_success.html')


def payment_error(request):
    print(request.GET)
    return render(request, 'purchases/payment_error.html', context={'products': []})


def payment_success(request):
    print('payment_success')
    print(request.GET)
    messages.success(request, 'You have successfully payment!')
    return render(request, 'purchases/payment_success.html', context={'products': []})


def checkout_view(request):
    intent = stripe.PaymentIntent.create(
        amount=1000,  # amount in cents
        currency='usd'
    )
    print('intent', intent)
    return render(
        request,
        'purchases/test_checkout.html',
        {'client_secret': intent.client_secret, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY}
    )


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



