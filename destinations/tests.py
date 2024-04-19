from django.test import TestCase
from django.urls import reverse, resolve

from .models import Destination, FAQDestination, ParentDestination
from products.models import Language
from .views import DestinationListView, DestinationDetailView


class DestinationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        parent_destination = ParentDestination.objects.create(parent_name='Test Parent Destination')

    def setUp(self):
        # Set up objects used by the test methods in this class
        language = Language.objects.create(name='English', code='EN')
        self.destination = Destination.objects.create(
            parent_destination=ParentDestination.objects.first(),
            name='Test Destination',
            main_title='<h2>Test Destination</h2>',
            language=language,
            is_active=True,
            slug='test-destination'
            # Add other required fields here
        )

    def test_display_main_title(self):
        self.assertEqual(self.destination.display_main_title(), '<h2>Test Destination</h2>')

    # Add more test methods for other model methods and properties


class DestinationViewTestCase(TestCase):
    fixtures = [
        'products/fixtures/testing/languages.json',
        'destinations/fixtures/testing/destinations.json'
    ]

    def setUp(self):
        pass

    def test_destination_list_view(self):
        response = self.client.get(reverse('destination-list', kwargs={'lang': 'en'}))
        self.assertEqual(response.status_code, 200)

    def test_destination_detail_view(self):
        response = self.client.get(reverse('destination-detail', kwargs={'lang': 'en', 'slug': 'lisbon-test-destination-en-lang'}))
        self.assertEqual(response.status_code, 200)


class DestinationsURLTestCase(TestCase):
    def test_destinations_list_url_resolve(self):
        url = reverse('destination-list', kwargs={'lang': 'en'})
        self.assertEqual(resolve(url).func.view_class, DestinationListView)

    def test_destinations_detail_url_resolve(self):
        url = reverse('destination-detail', kwargs={'lang': 'en', 'slug': 'test-destination'})
        self.assertEqual(resolve(url).func.view_class, DestinationDetailView)


class FAQDestinationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        parent_destination = ParentDestination.objects.create(parent_name='Test Parent Destination')
        language = Language.objects.create(name='English', code='EN')
        destination = Destination.objects.create(
            parent_destination=parent_destination,
            name='Test Destination',
            language=language,
            is_active=True,
            slug='test-destination'
        )

    def setUp(self):
        # Set up objects used by the test methods in this class
        self.faq_destination = FAQDestination.objects.create(
            destination=Destination.objects.first(),
            language=Language.objects.first(),
            question='Test Question',
            answer='<p>Test Answer</p>',
            is_active=True
            # Add other required fields here
        )

    def test_display_answer(self):
        self.assertEqual(self.faq_destination.display_answer(), '<p>Test Answer</p>')

    # Add more test methods for other model methods and properties
