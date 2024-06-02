from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch, Mock

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from schedule.models import Calendar

from accounts.models import User, Profile
from products.models import Product, ParentExperience, Experience, Language
from purchases.models import Purchase
from django.conf import settings
import stripe
import json


class BillingDetailViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('payment-form', kwargs={'lang': 'en'})
        self.user = User.objects.create_user('test-user@example.com')

        # Create a session and store the session key
        session = self.client.session
        session['key'] = 'value'
        session.save()
        self.session_key = session.session_key

        # create a parent experience
        self.private_parent_experience = ParentExperience.objects.create(
            parent_name='Test Private Parent Experience',
            price=Decimal(1000),
            is_private=True,
        )
        self.private_calendar = Calendar.objects.get_calendars_for_object(self.private_parent_experience).first()

        start = timezone.now() + timedelta(days=2)
        self.product = Product.objects.create(
            customer=self.user,
            session_key=self.session_key,
            parent_experience=self.private_parent_experience,
            total_price=1000,
            status='Pending',
            start_datetime=start,
        )

    def test_billing_detail_view_context(self):
        # Pass the session key to the client
        self.client.cookies['sessionid'] = self.session_key
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_sum', response.context)
        self.assertIn('product_ids', response.context)
        self.assertIn('stripe_public_key', response.context)
        self.assertIn('return_url', response.context)


# class StripeWebhookTests(TestCase):
#
#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('stripe-webhook')
#
#     @patch('stripe.Event.construct_from')
#     def test_stripe_webhook_payment_intent_succeeded(self, mock_construct_from):
#         event_data = {
#             'id': 'evt_test',
#             'type': 'payment_intent.succeeded',
#             'data': {
#                 'object': {
#                     'id': 'pi_test'
#                 }
#             }
#         }
#         mock_event = Mock(spec=stripe.Event, **event_data)
#         mock_construct_from.return_value = mock_event
#
#         response = self.client.post(self.url, json.dumps(event_data), content_type='application/json')
#         self.assertEqual(response.status_code, 200)
#
#     @patch('stripe.Event.construct_from')
#     def test_stripe_webhook_payment_intent_failed(self, mock_construct_from):
#         event_data = {
#             'id': 'evt_test',
#             'type': 'payment_intent.payment_failed',
#             'data': {
#                 'object': {
#                     'id': 'pi_test',
#                     'last_payment_error': {
#                         'code': 'test_error',
#                         'message': 'Test error message',
#                         'payment_method': {
#                             'billing_details': {
#                                 'name': 'Test User',
#                                 'email': 'test@example.com',
#                                 'phone': '1234567890',
#                                 'address': {
#                                     'city': 'Test City',
#                                     'country': 'Test Country',
#                                     'line1': 'Test Line1',
#                                     'line2': 'Test Line2',
#                                     'postal_code': '12345',
#                                     'state': 'Test State'
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#         mock_event = Mock(spec=stripe.Event, **event_data)
#         mock_construct_from.return_value = mock_event
#
#         response = self.client.post(self.url, json.dumps(event_data), content_type='application/json')
#         self.assertEqual(response.status_code, 200)


class CheckoutPaymentIntentViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('checkout-payment-intent')
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.profile = Profile.objects.create(
            user=self.user,
            name='Test User',
            email=self.user.email,
            stripe_customer_id='cs_outstripped',
        )

        # Create a session and store the session key
        session = self.client.session
        session['key'] = 'value'
        session.save()
        self.session_key = session.session_key

        # create a parent experience
        self.private_parent_experience = ParentExperience.objects.create(
            parent_name='Test Private Parent Experience',
            price=Decimal(1000),
            is_private=True,
        )
        self.private_calendar = Calendar.objects.get_calendars_for_object(self.private_parent_experience).first()

        start = timezone.now() + timedelta(days=2)
        self.product = Product.objects.create(
            customer=self.user,
            session_key=self.session_key,
            parent_experience=self.private_parent_experience,
            total_price=1000,
            status='Pending',
            start_datetime=start,
        )
        self.data = {
            'product_ids': [self.product.id]
        }

    @patch('stripe.PaymentIntent.create')
    def test_checkout_payment_intent_view_authenticated(self, mock_create):
        mock_create.return_value = Mock(id='pi_test', client_secret='secret_test', amount=1000)
        self.client.login(email='testuser@example.com', password='testpass')
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('clientSecret', response.json())
        self.assertIn('customerData', response.json())
        self.assertIn('paymentAmount', response.json())

    @patch('stripe.PaymentIntent.create')
    def test_checkout_payment_intent_view_unauthenticated(self, mock_create):
        mock_create.return_value = Mock(id='pi_test', client_secret='secret_test', amount=1000)
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('clientSecret', response.json())
        self.assertIn('customerData', response.json())
        self.assertIn('paymentAmount', response.json())


class ConfirmationViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('confirmation', kwargs={'lang': 'en'})
        self.user = User.objects.create_user('test-user@example.com')
        self.language = Language.objects.create(code='EN', name='English')
        # create a parent experience
        self.private_parent_experience = ParentExperience.objects.create(
            parent_name='Test Private Parent Experience',
            price=Decimal(1000),
            is_private=True,
        )
        self.private_parent_experience.allowed_languages.add(self.language)
        self.private_calendar = Calendar.objects.get_calendars_for_object(self.private_parent_experience).first()

        self.experience = Experience.objects.create(
            parent_experience=self.private_parent_experience,
            language=self.language,

        )

        start = timezone.now() + timedelta(days=2)
        self.product = Product.objects.create(
            customer=self.user,
            parent_experience=self.private_parent_experience,
            language=self.language,
            total_price=1000,
            status='Pending',
            start_datetime=start,
        )
        self.purchase = Purchase.objects.create(stripe_payment_intent_id='pi_test')
        self.purchase.products.set([self.product])

    def test_confirmation_view_with_payment_intent_id(self):
        response = self.client.get(self.url, {'payment_intent_id': 'pi_test'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('purchase', response.context)
        self.assertIn('object_list', response.context)
        self.assertIn('ecommerce_items', response.context)

    def test_confirmation_view_without_payment_intent_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payment-form', kwargs={'lang': 'en'}), status_code=302, target_status_code=302)
