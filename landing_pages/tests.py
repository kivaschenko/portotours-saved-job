from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.urls import reverse, resolve
from datetime import timedelta
from schedule.models import Calendar
from products.models import Experience, ParentExperience, ExperienceEvent, Language, ExperienceCategory, TimeOfDay, DurationForExperience
from reviews.models import Testimonial
from destinations.models import Destination
from .models import LandingPage
from .views import LandingPageView


class LandingPageViewTest(TestCase):
    fixtures = [
        'accounts/fixtures/testing/users.json',
        'products/fixtures/testing/languages.json',
        'products/fixtures/testing/filters.json',
        'destinations/fixtures/testing/destinations.json'
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.lang_en = Language.objects.filter(code='EN').first()
        self.wine_category = ExperienceCategory.objects.create(name='Wine Tasting Porto')
        self.walking_category = ExperienceCategory.objects.create(name='Walking Adventures')
        self.lisbon = Destination.objects.filter(slug="lisbon-test-destination-en-lang").first()

        self.wine_parent_experience = ParentExperience(
            parent_name="Wine Tour from Lisbon Test",
            priority_number=100,
            price=Decimal('100.00'),
            old_price=Decimal('133.00'),
            child_price=Decimal('50.00'),
            child_old_price=Decimal('80.00'),
        )
        self.wine_parent_experience.save()
        languages = Language.objects.filter(code__in=["EN", "FR", "PT"])
        self.wine_parent_experience.allowed_languages.set(languages)
        self.wine_parent_experience.categories.set([self.wine_category, self.walking_category])
        self.wine_parent_experience.time_of_day.set([TimeOfDay.objects.get(name='evening'), TimeOfDay.objects.get(name='afternoon')])
        self.wine_parent_experience.duration.set([DurationForExperience.objects.get(name='1-4'), DurationForExperience.objects.get(name='4-10')])

        self.wine_calendar = Calendar.objects.get_calendar_for_object(self.wine_parent_experience)

        self.experience_wine = Experience(
            parent_experience=self.wine_parent_experience,
            name="Wine Tour from Lisbon Experience Test",
            language=self.lang_en,
        )
        self.experience_wine.save()
        self.experience_wine.destinations.set([self.lisbon])

        self.walking_parent_experience = ParentExperience(
            parent_name="Walking Adventures Lisbon Test",
            priority_number=200,
            price=Decimal('50.00'),
            old_price=Decimal('75.00'),
            is_private=True,
            max_participants=4,
        )
        self.walking_parent_experience.save()
        self.walking_parent_experience.allowed_languages.set(languages)
        self.walking_parent_experience.categories.set([self.walking_category])

        self.walk_calendar = Calendar.objects.get_calendar_for_object(self.walking_parent_experience)

        self.experience_walk = Experience(
            parent_experience=self.walking_parent_experience,
            name='Lisbon walking tour test',
            language=self.lang_en,
        )
        self.experience_walk.save()
        self.experience_walk.destinations.set([self.lisbon.id])

        tomorrow = timezone.now() + timedelta(days=1)

        # Morning event (before 12 PM)
        morning_start = tomorrow.replace(hour=9, minute=30, second=0, microsecond=0)

        self.event_wine_morning_6_hours = ExperienceEvent.objects.create(
            calendar=self.wine_calendar,
            start=morning_start,
            end=morning_start + timedelta(hours=6),
            max_participants=10,
            remaining_participants=5,
            special_price=Decimal('50.00'),
        )

        # Afternoon event (12 PM to 5 PM)
        afternoon_start = tomorrow.replace(hour=13, minute=0, second=0, microsecond=0)

        self.event_wine_afternoon_30_hours = ExperienceEvent.objects.create(
            calendar=self.wine_calendar,
            start=afternoon_start,
            end=afternoon_start + timedelta(hours=30),
            max_participants=10,
            remaining_participants=5,
            special_price=Decimal('50.00'),
        )

        # Evening event (after 5 PM)
        evening_start = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)

        self.event_wine_evening_3_hours = ExperienceEvent.objects.create(
            calendar=self.wine_calendar,
            start=evening_start,
            end=evening_start + timedelta(hours=3),
            max_participants=10,
            remaining_participants=5,
        )

        self.event_walk_evening_3_hours = ExperienceEvent.objects.create(
            calendar=self.walk_calendar,
            start=evening_start,
            end=evening_start + timedelta(hours=3),
            max_participants=10,
        )

        self.landing_page = LandingPage.objects.create(
            title='Test Landing Page',
            slug='test-landing-page',
            language=self.lang_en,
            category=self.wine_category,
        )
        self.landing_page.destinations.set([self.lisbon])

        self.testimonial = Testimonial.objects.create(short_text='Great experince!')

    def test_landing_page_list_view(self):
        response = self.client.get(reverse('landing-page', kwargs={'slug': 'test-landing-page', 'lang': 'en'}))
        self.assertEqual(response.status_code, 200)

    def test_get_context_data_filter_evening_3_hours_lisbon(self):
        request = self.factory.get(reverse('landing-page', kwargs={'slug': 'test-landing-page', 'lang': 'en'}), {
            'destination': "lisbon-test-destination-en-lang",
            'tour_type': 'all',
            'time_of_day': 'evening',
            'duration': '1-4',
            'filter_by': 'all',
        })

        response = LandingPageView.as_view()(request, slug='test-landing-page', lang='en')
        context = response.context_data

        # Check if the correct experiences are returned
        self.assertIn('experiences', context)
        self.assertEqual(len(context['experiences']), 1)
        self.assertEqual(context['experiences'][0], self.experience_wine)

        # Check if testimonials are included
        self.assertIn('testimonials', context)
        self.assertEqual(len(context['testimonials']), 1)
        self.assertEqual(context['testimonials'][0], self.testimonial)

        # Check if destinations are included
        self.assertIn('select_destinations', context)
        self.assertEqual(len(context['select_destinations']), 1)
        self.assertEqual(context['select_destinations'][0][0], 'lisbon-test-destination-en-lang')

    def test_get_context_data_filter_duration_6_hours(self):
        request = self.factory.get(reverse('landing-page', kwargs={'slug': 'test-landing-page', 'lang': 'en'}), {
            'destination': 'all',
            'tour_type': 'all',
            'time_of_day': 'all',
            'duration': '4-10',
            'filter_by': 'all',
        })

        response = LandingPageView.as_view()(request, slug='test-landing-page', lang='en')
        context = response.context_data

        # Check if the correct experiences are returned
        self.assertIn('experiences', context)
        self.assertEqual(len(context['experiences']), 1)
        self.assertEqual(context['experiences'][0], self.experience_wine)

    def test_get_context_data_filter_afternoon(self):
        request = self.factory.get(reverse('landing-page', kwargs={'slug': 'test-landing-page', 'lang': 'en'}), {
            'destination': "lisbon-test-destination-en-lang",
            'tour_type': 'all',
            'time_of_day': 'afternoon',
            'duration': 'all',
            'filter_by': 'all',
        })

        response = LandingPageView.as_view()(request, slug='test-landing-page', lang='en')
        context = response.context_data

        # Check if the correct experiences are returned
        self.assertIn('experiences', context)
        self.assertEqual(len(context['experiences']), 1)
        self.assertEqual(context['experiences'][0], self.experience_wine)

    def test_get_context_data_filter_empty_result(self):
        request = self.factory.get(reverse('landing-page', kwargs={'slug': 'test-landing-page', 'lang': 'en'}), {
            'destination': 'lisbon',
            'tour_type': 'all',
            'time_of_day': 'afternoon',
            'duration': '1-4',
            'filter_by': 'all',
        })

        response = LandingPageView.as_view()(request, slug='test-landing-page', lang='en')
        context = response.context_data

        # Check if the correct experiences are returned
        self.assertIn('experiences', context)
        self.assertEqual(len(context['experiences']), 0)


class LandingPageURLTestcase(TestCase):
    def test_landing_page_url_resolve(self):
        url = reverse('landing-page', kwargs={'slug': 'test-landing-page', 'lang': 'en'})
        self.assertEqual(resolve(url).func.view_class, LandingPageView)
