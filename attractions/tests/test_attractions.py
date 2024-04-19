from django.test import TestCase, RequestFactory
from django.test import SimpleTestCase
from django.urls import reverse, resolve

from attractions.views import AttractionListView, AttractionDetailView
from attractions.models import Attraction, ParentAttraction, TagAttraction, FAQAttraction


class AttractionModelTestCase(TestCase):
    fixtures = [
        'products/fixtures/testing/languages.json',
    ]

    def setUp(self):
        # Create test objects as needed
        pass

    def test_attraction_str_method(self):
        attraction = Attraction.objects.create(name="Test Attraction", language_id=1)
        self.assertEqual(str(attraction), "Test Attraction (English)")

    # Add more test methods as needed for other model functionalities


# Similarly, write test cases for other models: ParentAttraction, TagAttraction, FAQAttraction
# test_attractions.py inside your attractions app directory


class AttractionViewTestCase(TestCase):
    fixtures = [
        'products/fixtures/testing/languages.json',
        'attractions/fixtures/testing/attractions.json',
    ]

    def setUp(self):
        pass

    def test_attraction_list_view(self):
        response = self.client.get(reverse('attraction-list', kwargs={'lang': 'en'}))
        self.assertEqual(response.status_code, 200)
        # Add more assertions as needed

    def test_attraction_details_view(self):
        response = self.client.get(reverse('attraction-detail', kwargs={'lang': 'en', 'slug': "st-georges-castle-lisbon"}))
        self.assertEqual(response.status_code, 200)


class AttractionsURLTestCase(SimpleTestCase):
    def test_attraction_list_url_resolves(self):
        url = reverse('attraction-list', kwargs={'lang': 'en'})
        self.assertEqual(resolve(url).func.view_class, AttractionListView)

    def test_attraction_details_url_resolves(self):
        url = reverse('attraction-detail', kwargs={'lang': 'en', 'slug': "st-georges-castle-lisbon"})
        self.assertEqual(resolve(url).func.view_class, AttractionDetailView)
