from decimal import Decimal

from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.db.models.signals import post_save
from django.urls import reverse
from schedule.models import Calendar

from products.models import Product, ParentExperience, ExperienceEvent, Language, Occurrence
from products.signals import create_calendar, fill_empty_prices_and_set_relation


class TestCreateProductView(TestCase):
    fixtures = [
        'accounts/fixtures/testing/users.json',
        'destinations/fixtures/testing/destinations.json',
        'products/fixtures/testing/experiences.json',
        'products/fixtures/testing/languages.json'
    ]

    def setUp(self):
        self.client = Client()
        # Disable post_save signals
    #     post_save.disconnect(receiver=create_calendar, sender=ParentExperience)
    #     post_save.disconnect(receiver=fill_empty_prices_and_set_relation, sender=ExperienceEvent)
    #
    # def tearDown(self):
    #     # Reconnect post_save signal
    #     post_save.connect(receiver=create_calendar, sender=ParentExperience)
    #     post_save.connect(receiver=fill_empty_prices_and_set_relation, sender=ExperienceEvent)

    def test_create_product_post(self):
        # Create necessary objects for testing
        calendar = Calendar.objects.first()
        
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        exp_event = ExperienceEvent.objects.create(
            title='Test Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=calendar,
        )
        # Test POST request
        response = self.client.post(reverse('create-product'), {
            'adults': 2,
            'children': 1,
            'language': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': exp_event.id,
            'parent_experience_id': 1
        })

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Product.objects.count(), 1)

        new_product = Product.objects.first()

        self.assertEqual(new_product.start_datetime.replace(tzinfo=None), tomorrow.replace(tzinfo=None))
        self.assertEqual(str(new_product.adults_price), "50.00")
        self.assertEqual(new_product.adults_count, 2)
        self.assertEqual(str(new_product.child_price), "25.00")
        self.assertEqual(new_product.stripe_price, 12500)
        self.assertEqual(new_product.child_count, 1)
        self.assertEqual(new_product.status, 'Pending')

        self.assertEqual(Occurrence.objects.count(), 1)

    def test_create_product_get(self):
        # Test GET request
        response = self.client.get(reverse('create-product'))
        self.assertEqual(response.status_code, 405)

    def test_get_event_booking_data(self):
        # Create necessary objects for testing
        calendar = Calendar.objects.first()

        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        event = ExperienceEvent.objects.create(
            title='Test Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('89.99'),
            child_special_price=Decimal('44.99'),
            calendar=calendar,
        )

        # Test GET request
        response = self.client.get(reverse('experience-event-data', args=[event.id]))

        self.assertEqual(response.status_code, 200)

        expected_data = {'result': {str(event.id): {'date': event.start_date, 'time': event.start_time, 'adult_price': 89.99, 'child_price': 44.99,
                                                    'max_participants': 8, 'booked_participants': 0, 'remaining_participants': 8,
                                                    'experience_event_id': event.id}}}

        self.assertEqual(response.json(), expected_data)
