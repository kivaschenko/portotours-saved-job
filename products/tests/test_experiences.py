from decimal import Decimal
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
            happy_clients_number=50,
            free_cancellation=True,
            show_on_home_page=True,
            rating=Decimal('4.8')
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
        self.assertEqual(parent_experience.happy_clients_number, 50)
        self.assertTrue(parent_experience.show_on_home_page)
        self.assertEqual(parent_experience.rating, Decimal('4.8'))

        parent_experience.delete()


# class ExperienceViewTest(TestCase):
#     fixtures = [
#         'products/fixtures/testing/languages.json',
#         'products/fixtures/testing/experiences.json',
#     ]
#
#     def test_experiences_list_view(self):
#         response = self.client.get(reverse('experiences-list', kwargs={'lang': 'en'}))
#         self.assertEqual(response.status_code, 200)
#         print(response.content)
#
#     def test_experiences_details_view(self):
#         response = self.client.get(reverse('experiences-details', kwargs={'lang': 'en', 'slug': 'attractive-private-tour-about-lisbon'}))
#         self.assertEqual(response.status_code, 200)
#         print(response.content)