from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from products.models import Experience, ParentExperience, ExperienceEvent, Language
from schedule.models import Event, Calendar, EventRelation
from products.views import ExperienceListView

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse, resolve

from products.models import *  # noqa


class MeetingPointModelTest(TestCase):

    def test_meeting_point_auto_location_success(self):
        start_point = MeetingPoint(
            name='Lisbon Cathedral Test',
            country='Portugal',
            city='Lisbon',
            address='Sé Catedral de Lisboa, Largo da Sé',
            auto_location=True,
            update_coords_by_geom=False,
            auto_update_address_name=True,
        )
        start_point.save()
        drop_point = MeetingPoint(
            name='The Jeronimos Monastery Test',
            country='Portugal',
            address='The Jeronimos Monastery',
            auto_location=True,
            update_coords_by_geom=False,
            auto_update_address_name=True,
        )
        drop_point.save()
        # test names
        self.assertEqual('Lisbon Cathedral Test', start_point.name)
        self.assertEqual('The Jeronimos Monastery Test', drop_point.name)
        # test slugs
        self.assertEqual('lisbon-cathedral-test', start_point.slug)
        self.assertEqual('the-jeronimos-monastery-test', drop_point.slug)
        # test coords
        self.assertEqual(38.709839, round(start_point.latitude, 6))
        self.assertEqual(-9.132801, round(start_point.longitude, 6))
        self.assertEqual(38.697758, round(drop_point.latitude, 6))
        self.assertEqual(-9.206624, round(drop_point.longitude, 6))
        # test address
        self.assertIn('Sé Catedral de Lisboa, Largo da Sé', start_point.address)
        self.assertIn("Praça do Império, Belém, Lisboa, ", drop_point.address)

        start_point.delete()
        drop_point.delete()


class ParentExperienceModelTest(TestCase):
    fixtures = [
        'products/fixtures/testing/languages.json',
        'products/fixtures/testing/meeting_point.json',
    ]

    def test_parent_experience_created_success(self):
        parent_experience = ParentExperience(
            parent_name="Lisbon View Attractions Test",
            priority_number=11,
            price=Decimal('100.00'),
            old_price=Decimal('133.00'),
            child_price=Decimal('50.00'),
            child_old_price=Decimal('80.00'),
            meeting_point_id=1,
            drop_point_id=2,
            is_exclusive=True,
            free_cancellation=True,
            show_on_home_page=True,
        )
        parent_experience.save()
        languages = Language.objects.filter(code__in=["EN", "FR", "PT"])
        parent_experience.allowed_languages.set(languages)

        self.assertEqual(parent_experience.price, Decimal('100.00'))
        self.assertEqual(parent_experience.old_price, Decimal('133.00'))
        self.assertEqual(parent_experience.increase_percentage_old_price, 25)
        self.assertEqual(parent_experience.child_price, Decimal('50.00'))
        self.assertEqual(parent_experience.child_old_price, Decimal('80.00'))
        self.assertEqual(parent_experience.child_discount, 50)
        self.assertEqual(parent_experience.currency, 'eur')
        self.assertEqual(parent_experience.slug, "lisbon-view-attractions-test")
        self.assertEqual(parent_experience.priority_number, 11)
        self.assertEqual(parent_experience.meeting_point.address,
                         "Sé Catedral de Lisboa, Largo da Sé, Sé, Alfama, Santa Maria Maior, Lisboa, 1100-501, Portugal")
        self.assertEqual(parent_experience.drop_point.address, "Praça do Império, Belém, Lisboa, 1400-209, Portugal")
        self.assertEqual(parent_experience.max_participants, 8)
        self.assertFalse(parent_experience.is_private)
        self.assertTrue(parent_experience.is_exclusive)
        self.assertFalse(parent_experience.is_hot_deals)
        self.assertEqual(parent_experience.allowed_languages.count(), 3)
        self.assertTrue(parent_experience.free_cancellation)
        self.assertTrue(parent_experience.show_on_home_page)

        parent_experience.delete()


# class ExperienceListViewTest(TestCase):
#     fixtures = ['accounts/fixtures/testing/users.json']
#
#     def setUp(self):
#         # Create a Language instance
#         self.language = Language.objects.create(code='EN', name='English')
#
#         # Create a ParentExperience instance
#         self.parent_experience = ParentExperience.objects.create(
#             parent_name='Parent Experience Test',
#             price=100,
#             is_private=False,
#         )
#         self.parent_experience.allowed_languages.add(self.language)
#
#         # Create an Experience instance
#         self.experience = Experience.objects.create(
#             name='Experience Test',
#             parent_experience=self.parent_experience,
#             language=self.language,
#         )
#
#         # Create a Calendar instance
#         self.calendar = Calendar.objects.get_calendars_for_object(self.parent_experience).first()
#
#         # Create an ExperienceEvent instance
#         start_datetime = timezone.now() + timezone.timedelta(days=5)
#         end_datetime = start_datetime + timezone.timedelta(hours=2)
#         self.event = ExperienceEvent.objects.create(
#             start=start_datetime,
#             end=end_datetime,
#             title='Test Event',
#             remaining_participants=10,
#             calendar=self.calendar,
#         )
#
#         self.factory = RequestFactory()
#
#     def tearDown(self):
#         self.language.delete()
#         self.parent_experience.delete()
#         self.experience.delete()
#         self.event.delete()
#
#     def test_experience_list_view(self):
#         search_date = timezone.now() + timezone.timedelta(days=3)
#         # Create a request
#         request = self.factory.get(reverse('experience-list', kwargs={'lang': 'en'}), {'place': '', 'date': search_date.strftime('%Y-%m-%d')})
#
#         # Get the response
#         response = ExperienceListView.as_view()(request)
#
#         # Check the response status code
#         self.assertEqual(response.status_code, 200)
#
#         # Check if the remaining_participants attribute is in the context data
#         self.assertIn('object_list', response.context_data)
#         object_list = response.context_data['object_list']
#         self.assertTrue(len(object_list) > 0)
#
#         experience = object_list[0]
#         self.assertTrue(hasattr(experience, 'remaining_participants'))
#         self.assertEqual(experience.remaining_participants, 10)
