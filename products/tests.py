from django.test import TestCase, Client
from django.db.models.signals import post_save
from django.urls import reverse
from products.models import Product, ParentExperience, ExperienceEvent, Language, Occurrence
from products.signals import create_calendar, fill_empty_prices_and_set_relation


class TestCreateProductView(TestCase):
    fixtures = [
        'products/fixtures/testing/experiences.json',
        'products/fixtures/testing/languages.json'
    ]

    def setUp(self):
        self.client = Client()
        # Disable post_save signals
        post_save.disconnect(receiver=create_calendar, sender=ParentExperience)
        post_save.disconnect(receiver=fill_empty_prices_and_set_relation, sender=ExperienceEvent)

    def tearDown(self):
        # Reconnect post_save signal
        post_save.connect(receiver=create_calendar, sender=ParentExperience)
        post_save.connect(receiver=fill_empty_prices_and_set_relation, sender=ExperienceEvent)

    def test_create_product_post(self):
        # Test POST request
        response = self.client.post(reverse('create-product'), {
            'adults': 2,
            'children': 1,
            'language': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': 19,
            'parent_experience_id': 1
        })

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Product.objects.count(), 1)

        new_product = Product.objects.first()
        self.assertEqual(new_product.start_datetime, "2024-03-22T09:00:00Z")
        self.assertEqual(str(new_product.adults_price), "45.99")
        self.assertEqual(new_product.adults_count, 2)
        self.assertEqual(str(new_product.child_price), "30.81")
        self.assertEqual(new_product.child_count, 1)
        self.assertEqual(new_product.status, 'Pending')

        self.assertEqual(Occurrence.objects.count(), 1)

    def test_create_product_get(self):
        # Test GET request
        response = self.client.get(reverse('create-product'))
        self.assertEqual(response.status_code, 405)
