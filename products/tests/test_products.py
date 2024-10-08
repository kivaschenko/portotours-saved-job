import json
from decimal import Decimal

from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from schedule.models import Calendar

from products.models import Product, ParentExperience, ExperienceEvent, Language, Occurrence, ProductOption, ExperienceOption


class TestProductLogic(TestCase):
    fixtures = [
        'accounts/fixtures/testing/users.json',
        'destinations/fixtures/testing/destinations.json',
        'products/fixtures/testing/languages.json',
        'products/fixtures/testing/meeting_point.json'
    ]

    def setUp(self):
        self.client = Client()
        # create group ParentExperience
        self.group_parent_experience = ParentExperience.objects.create(
            parent_name='Test Group Parent Experience',
            priority_number=1,
            price=Decimal('39.99'),
            use_auto_increase_old_price=True,
            meeting_point_id=1,
            is_exclusive=True
        )
        self.group_parent_experience.allowed_languages.add(Language.objects.get(id=1), Language.objects.get(id=2), Language.objects.get(id=3))
        # create private ParentExperience
        self.private_parent_experience = ParentExperience.objects.create(
            parent_name='Test Private Parent Experience',
            priority_number=2,
            price=Decimal('499.99'),
            use_auto_increase_old_price=True,
            meeting_point_id=2,
            is_private=True,
            is_exclusive=True,
        )
        self.private_parent_experience.allowed_languages.add(Language.objects.get(id=1), Language.objects.get(id=4))
        # calendars
        self.group_calendar = Calendar.objects.get_calendars_for_object(self.group_parent_experience).first()
        self.private_calendar = Calendar.objects.get_calendars_for_object(self.private_parent_experience).first()

    def test_create_group_product_post(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_group_event.id,
            'parent_experience_id': self.group_parent_experience.id
        }
        response = self.client.post(reverse('create-product'), data=json.dumps(data), content_type='application/json')
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
        response = self.client.get(reverse('create-product'))
        self.assertEqual(response.status_code, 405)

    def test_all_group_actual_events(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        end_yesterday = yesterday + timedelta(hours=1)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        yesterday_group_event = ExperienceEvent.objects.create(
            title='Test Yesterday Group Event',
            start=yesterday,
            end=end_yesterday,
            special_price=Decimal('49.99'),
            child_special_price=Decimal('24.99'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event_2 = ExperienceEvent.objects.create(
            title='Test Group Event 2',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('67.99'),
            child_special_price=Decimal('33.99'),
            calendar=self.group_calendar,
        )
        response = self.client.get(reverse('actual-experience-events', args=[self.group_parent_experience.id]))
        self.assertEqual(response.status_code, 200)
        result = response.json()['result']
        self.assertEqual(result['languages'], ['EN', 'ES', 'FR'])
        current_date = datetime.today().date()
        for event in result['events']:
            date_string = event['date']
            date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
            self.assertGreaterEqual(date_object, current_date)

    def test_group_update_product(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event_2 = ExperienceEvent.objects.create(
            title='Test Group Event 2',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('67.99'),
            child_special_price=Decimal('33.99'),
            calendar=self.group_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_group_event.id,
            'parent_experience_id': self.group_parent_experience.id
        }
        response = self.client.post(reverse('create-product'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        product = Product.objects.first()
        update_data = {
            'adults': 3,
            'children': 2,
            'language_code': 'ES',
            'event_id': tomorrow_group_event_2.id,
            'product_id': product.id
        }
        response = self.client.post(reverse('update-product'), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        updated_product = Product.objects.get(id=product.id)
        self.assertEqual(updated_product.adults_count, 3)
        self.assertEqual(updated_product.child_count, 2)
        self.assertEqual(updated_product.language.code, 'ES')
        self.assertEqual(updated_product.start_datetime.replace(tzinfo=None), tomorrow_group_event_2.start.replace(tzinfo=None))
        self.assertEqual(updated_product.adults_price, tomorrow_group_event_2.special_price)
        self.assertEqual(updated_product.child_price, tomorrow_group_event_2.child_special_price)

    def test_cancel_group_product(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('59.99'),
            child_special_price=Decimal('29.99'),
            calendar=self.group_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session35813',
            'event_id': tomorrow_group_event.id,
            'parent_experience_id': self.group_parent_experience.id
        }
        response = self.client.post(reverse('create-product'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        occur_pk = product.occurrence.pk
        updated_event = ExperienceEvent.objects.get(id=tomorrow_group_event.id)
        self.assertEqual(updated_event.booked_participants, 3)
        self.assertEqual(updated_event.remaining_participants, 5)
        self.assertIsInstance(product.occurrence, Occurrence)
        response = self.client.delete(reverse('cancel-product', kwargs={'pk': product.pk}))

        self.assertEqual(response.status_code, 302)

        cancelled_product = Product.objects.get(pk=product.pk)
        cancelled_event = ExperienceEvent.objects.get(id=updated_event.id)
        cancelled_occurrence = Occurrence.objects.get(pk=occur_pk)
        self.assertEqual(cancelled_product.status, 'Cancelled')
        self.assertEqual(cancelled_event.booked_participants, 0)
        self.assertEqual(cancelled_event.remaining_participants, 8)
        self.assertTrue(cancelled_occurrence.cancelled)

    def test_create_private_product_post(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('499.99'),
            calendar=self.private_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_private_event.id,
            'parent_experience_id': self.private_parent_experience.id
        }
        response = self.client.post(reverse('create-private-product'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        new_product = Product.objects.first()
        self.assertEqual(new_product.start_datetime.replace(tzinfo=None), tomorrow.replace(tzinfo=None))
        self.assertEqual(new_product.total_price, Decimal('499.99'))
        self.assertEqual(new_product.adults_count, 2)
        self.assertEqual(new_product.stripe_price, 49999)
        self.assertEqual(new_product.child_count, 1)
        self.assertEqual(new_product.status, 'Pending')
        self.assertEqual(Occurrence.objects.count(), 1)

    def test_create_private_product_get(self):
        response = self.client.get(reverse('create-private-product'))
        self.assertEqual(response.status_code, 405)

    def test_all_private_actual_events(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        end_yesterday = yesterday + timedelta(hours=1)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        yesterday_private_event = ExperienceEvent.objects.create(
            title='Test Yesterday Private Event',
            start=yesterday,
            end=end_yesterday,
            total_price=Decimal('399.99'),
            calendar=self.private_calendar,
        )
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('499.99'),
            calendar=self.private_calendar,
        )
        tomorrow_private_event_2 = ExperienceEvent.objects.create(
            title='Test Private Event 2',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('599.99'),
            calendar=self.private_calendar,
        )
        response = self.client.get(reverse('actual-experience-events', args=[self.private_parent_experience.id]))
        self.assertEqual(response.status_code, 200)
        result = response.json()['result']
        self.assertEqual(result['languages'], ['EN', 'PT'])
        current_date = datetime.today().date()
        for event in result['events']:
            date_string = event['date']
            date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
            self.assertGreaterEqual(date_object, current_date)

    def test_private_update_product(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('499.99'),
            calendar=self.private_calendar,
        )
        tomorrow_private_event_2 = ExperienceEvent.objects.create(
            title='Test Private Event 2',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('599.99'),
            calendar=self.private_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_private_event.id,
            'parent_experience_id': self.private_parent_experience.id
        }
        response = self.client.post(reverse('create-private-product'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        product = Product.objects.first()
        update_data = {
            'adults': 3,
            'children': 2,
            'language_code': 'ES',
            'event_id': tomorrow_private_event_2.id,
            'product_id': product.id
        }
        response = self.client.post(reverse('update-private-product'), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        updated_product = Product.objects.get(id=product.id)
        self.assertEqual(updated_product.adults_count, 3)
        self.assertEqual(updated_product.child_count, 2)
        self.assertEqual(updated_product.language.code, 'ES')
        self.assertEqual(updated_product.start_datetime.replace(tzinfo=None), tomorrow_private_event_2.start.replace(tzinfo=None))
        self.assertEqual(updated_product.total_price, tomorrow_private_event_2.total_price)

    def test_cancel_private_product(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('499.99'),
            calendar=self.private_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_private_event.id,
            'parent_experience_id': self.private_parent_experience.id
        }
        response = self.client.post(reverse('create-private-product'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        occur_pk = product.occurrence.pk
        updated_event = ExperienceEvent.objects.get(id=tomorrow_private_event.id)
        self.assertEqual(updated_event.booked_participants, 3)
        self.assertEqual(updated_event.remaining_participants, 5)
        self.assertIsInstance(product.occurrence, Occurrence)
        response = self.client.delete(reverse('cancel-product', kwargs={'pk': product.pk}))

        self.assertEqual(response.status_code, 302)

        cancelled_product = Product.objects.get(pk=product.pk)
        cancelled_event = ExperienceEvent.objects.get(id=updated_event.id)
        cancelled_occurrence = Occurrence.objects.get(pk=occur_pk)
        self.assertEqual(cancelled_product.status, 'Cancelled')
        self.assertEqual(cancelled_event.booked_participants, 0)
        self.assertEqual(cancelled_event.remaining_participants, 8)
        self.assertTrue(cancelled_occurrence.cancelled)


# -------------------------
# Fake booking products test

class TestFakeBookingProductLogic(TestCase):
    """The logic for testing fake booking product."""
    fixtures = [
        'accounts/fixtures/testing/users.json',
        'destinations/fixtures/testing/destinations.json',
        'products/fixtures/testing/languages.json',
        'products/fixtures/testing/meeting_point.json'
    ]

    def setUp(self):
        self.client = Client()
        # create group ParentExperience
        self.group_parent_experience = ParentExperience.objects.create(
            parent_name='Test Group Parent Experience',
            priority_number=1,
            price=Decimal('39.99'),
            use_auto_increase_old_price=True,
            meeting_point_id=1,
            is_exclusive=True
        )
        self.group_parent_experience.allowed_languages.add(Language.objects.get(id=1), Language.objects.get(id=2), Language.objects.get(id=3))
        # create private ParentExperience
        self.private_parent_experience = ParentExperience.objects.create(
            parent_name='Test Private Parent Experience',
            priority_number=2,
            price=Decimal('499.99'),
            use_auto_increase_old_price=True,
            meeting_point_id=2,
            is_private=True,
            is_exclusive=True,
        )
        self.private_parent_experience.allowed_languages.add(Language.objects.get(id=1), Language.objects.get(id=4))
        # calendars
        self.group_calendar = Calendar.objects.get_calendars_for_object(self.group_parent_experience).first()
        self.private_calendar = Calendar.objects.get_calendars_for_object(self.private_parent_experience).first()

        self.option_first = ExperienceOption.objects.create(
            name='test_option_first',
            price=Decimal('5.00'),
        )
        self.option_second = ExperienceOption.objects.create(
            name='test_option_second',
            price=Decimal('10.00'),
        )
        self.option_unused = ExperienceOption.objects.create(
            name='test_option_unused',
            price=Decimal('3.00'),
        )


    def test_create_group_product_without_booking_post(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_group_event.id,
            'parent_experience_id': self.group_parent_experience.id
        }
        response = self.client.post(reverse('create-group-product-without-booking'), data=json.dumps(data), content_type='application/json')
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

    def test_create_group_product_without_booking_get(self):
        response = self.client.get(reverse('create-product'))
        self.assertEqual(response.status_code, 405)

    def test_all_group_actual_events(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        end_yesterday = yesterday + timedelta(hours=1)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        yesterday_group_event = ExperienceEvent.objects.create(
            title='Test Yesterday Group Event',
            start=yesterday,
            end=end_yesterday,
            special_price=Decimal('49.99'),
            child_special_price=Decimal('24.99'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event_2 = ExperienceEvent.objects.create(
            title='Test Group Event 2',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('67.99'),
            child_special_price=Decimal('33.99'),
            calendar=self.group_calendar,
        )
        response = self.client.get(reverse('actual-experience-events', args=[self.group_parent_experience.id]))
        self.assertEqual(response.status_code, 200)
        result = response.json()['result']
        self.assertEqual(result['languages'], ['EN', 'ES', 'FR'])
        current_date = datetime.today().date()
        for event in result['events']:
            date_string = event['date']
            date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
            self.assertGreaterEqual(date_object, current_date)

    def test_update_group_product_without_booking(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event_2 = ExperienceEvent.objects.create(
            title='Test Group Event 2',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('67.99'),
            child_special_price=Decimal('33.99'),
            calendar=self.group_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_group_event.id,
            'parent_experience_id': self.group_parent_experience.id
        }
        response = self.client.post(reverse('create-group-product-without-booking'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        product = Product.objects.first()
        update_data = {
            'adults': 3,
            'children': 2,
            'language_code': 'ES',
            'event_id': tomorrow_group_event_2.id,
            'product_id': product.id
        }
        response = self.client.post(reverse('update-group-product-without-booking'), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        updated_product = Product.objects.get(id=product.id)
        self.assertEqual(updated_product.adults_count, 3)
        self.assertEqual(updated_product.child_count, 2)
        self.assertEqual(updated_product.language.code, 'ES')
        self.assertEqual(updated_product.start_datetime.replace(tzinfo=None), tomorrow_group_event_2.start.replace(tzinfo=None))
        self.assertEqual(updated_product.adults_price, tomorrow_group_event_2.special_price)
        self.assertEqual(updated_product.child_price, tomorrow_group_event_2.child_special_price)

    def test_delete_group_product(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('59.99'),
            child_special_price=Decimal('29.99'),
            calendar=self.group_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session35813',
            'event_id': tomorrow_group_event.id,
            'parent_experience_id': self.group_parent_experience.id
        }
        response = self.client.post(reverse('create-product'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        occur_pk = product.occurrence.pk
        self.assertIsInstance(product.occurrence, Occurrence)
        response = self.client.delete(reverse('delete-product', kwargs={'pk': product.pk}))

        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=product.pk)
        with self.assertRaises(Occurrence.DoesNotExist):
            Occurrence.objects.get(pk=occur_pk)

    def test_create_private_product_without_booking_post(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('499.99'),
            calendar=self.private_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_private_event.id,
            'parent_experience_id': self.private_parent_experience.id
        }
        response = self.client.post(reverse('create-private-product-without-booking'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        new_product = Product.objects.first()
        self.assertEqual(new_product.start_datetime.replace(tzinfo=None), tomorrow.replace(tzinfo=None))
        self.assertEqual(new_product.total_price, Decimal('499.99'))
        self.assertEqual(new_product.adults_count, 2)
        self.assertEqual(new_product.stripe_price, 49999)
        self.assertEqual(new_product.child_count, 1)
        self.assertEqual(new_product.status, 'Pending')
        self.assertEqual(Occurrence.objects.count(), 1)

    def test_all_private_actual_events(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        end_yesterday = yesterday + timedelta(hours=1)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        yesterday_private_event = ExperienceEvent.objects.create(
            title='Test Yesterday Private Event',
            start=yesterday,
            end=end_yesterday,
            total_price=Decimal('399.99'),
            calendar=self.private_calendar,
        )
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('499.99'),
            calendar=self.private_calendar,
        )
        tomorrow_private_event_2 = ExperienceEvent.objects.create(
            title='Test Private Event 2',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('599.99'),
            calendar=self.private_calendar,
        )
        response = self.client.get(reverse('actual-experience-events', args=[self.private_parent_experience.id]))
        self.assertEqual(response.status_code, 200)
        result = response.json()['result']
        self.assertEqual(result['languages'], ['EN', 'PT'])
        current_date = datetime.today().date()
        for event in result['events']:
            date_string = event['date']
            date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
            self.assertGreaterEqual(date_object, current_date)

    def test_update_private_product_without_booking(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('499.99'),
            calendar=self.private_calendar,
        )
        tomorrow_private_event_2 = ExperienceEvent.objects.create(
            title='Test Private Event 2',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('599.99'),
            calendar=self.private_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_private_event.id,
            'parent_experience_id': self.private_parent_experience.id
        }
        response = self.client.post(reverse('create-private-product-without-booking'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        product = Product.objects.first()
        update_data = {
            'adults': 3,
            'children': 2,
            'language_code': 'ES',
            'event_id': tomorrow_private_event_2.id,
            'product_id': product.id
        }
        response = self.client.post(reverse('update-private-product-without-booking'), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        updated_product = Product.objects.get(id=product.id)
        self.assertEqual(updated_product.adults_count, 3)
        self.assertEqual(updated_product.child_count, 2)
        self.assertEqual(updated_product.language.code, 'ES')
        self.assertEqual(updated_product.start_datetime.replace(tzinfo=None), tomorrow_private_event_2.start.replace(tzinfo=None))
        self.assertEqual(updated_product.total_price, tomorrow_private_event_2.total_price)

    def test_delete_private_product(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('499.99'),
            calendar=self.private_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_private_event.id,
            'parent_experience_id': self.private_parent_experience.id
        }
        response = self.client.post(reverse('create-private-product'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        occur_pk = product.occurrence.pk
        self.assertIsInstance(product.occurrence, Occurrence)
        response = self.client.delete(reverse('delete-product', kwargs={'pk': product.pk}))

        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=product.pk)
        with self.assertRaises(Occurrence.DoesNotExist):
            Occurrence.objects.get(pk=occur_pk)

    def test_create_group_product_with_options_but_without_booking_post(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_group_event.id,
            'parent_experience_id': self.group_parent_experience.id,
            'options': [
                {'id': self.option_first.id, 'quantity': 1, 'price': float(self.option_first.price)},
                {'id': self.option_second.id, 'quantity': 2, 'price': float(self.option_second.price)},
            ],
        }
        response = self.client.post(reverse('create-group-product-without-booking'),
                                    data=json.dumps(data), content_type='application/json')
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
        product_options = new_product.options.all().order_by('quantity')
        self.assertEqual(len(product_options), 2)
        self.assertEqual(product_options.first().quantity, 1)
        self.assertEqual(product_options.first().total_sum, 5.00)
        self.assertEqual(product_options.last().quantity, 2)
        self.assertEqual(product_options.last().total_sum, 20.00)

    def test_create_group_product_without_booking_get(self):
        response = self.client.get(reverse('create-product'))
        self.assertEqual(response.status_code, 405)

    def test_all_group_actual_events(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        end_yesterday = yesterday + timedelta(hours=1)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        yesterday_group_event = ExperienceEvent.objects.create(
            title='Test Yesterday Group Event',
            start=yesterday,
            end=end_yesterday,
            special_price=Decimal('49.99'),
            child_special_price=Decimal('24.99'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event_2 = ExperienceEvent.objects.create(
            title='Test Group Event 2',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('67.99'),
            child_special_price=Decimal('33.99'),
            calendar=self.group_calendar,
        )
        response = self.client.get(reverse('actual-experience-events', args=[self.group_parent_experience.id]))
        self.assertEqual(response.status_code, 200)
        result = response.json()['result']
        self.assertEqual(result['languages'], ['EN', 'ES', 'FR'])
        current_date = datetime.today().date()
        for event in result['events']:
            date_string = event['date']
            date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
            self.assertGreaterEqual(date_object, current_date)
    def test_update_group_product_with_options_without_booking(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_group_event = ExperienceEvent.objects.create(
            title='Test Group Event',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('50.00'),
            child_special_price=Decimal('25.00'),
            calendar=self.group_calendar,
        )
        tomorrow_group_event_2 = ExperienceEvent.objects.create(
            title='Test Group Event 2',
            start=tomorrow,
            end=end_date,
            special_price=Decimal('67.99'),
            child_special_price=Decimal('33.99'),
            calendar=self.group_calendar,
        )
        data = {
            'adults': 2,
            'children': 1,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_group_event.id,
            'parent_experience_id': self.group_parent_experience.id,
            'options': [
                {'id': self.option_first.id, 'quantity': 1, 'price': float(self.option_first.price)},
                {'id': self.option_second.id, 'quantity': 2, 'price': float(self.option_second.price)},
                {'id': self.option_unused.id, 'quantity': 0, 'price': float(self.option_unused.price)},
            ],
        }
        response = self.client.post(reverse('create-group-product-without-booking'),
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        product = Product.objects.first()
        update_data = {
            'adults': 3,
            'children': 2,
            'language_code': 'ES',
            'event_id': tomorrow_group_event_2.id,
            'product_id': product.id,
            'options': [
                {'id': self.option_first.id, 'quantity': 0, 'price': float(self.option_first.price)},
                {'id': self.option_second.id, 'quantity': 3, 'price': float(self.option_second.price)},
                {'id': self.option_unused.id, 'quantity': 4, 'price': float(self.option_unused.price)},
            ],
        }
        response = self.client.post(reverse('update-group-product-without-booking'), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        updated_product = Product.objects.get(id=product.id)
        self.assertEqual(updated_product.adults_count, 3)
        self.assertEqual(updated_product.child_count, 2)
        self.assertEqual(updated_product.language.code, 'ES')
        self.assertEqual(updated_product.start_datetime.replace(tzinfo=None), tomorrow_group_event_2.start.replace(tzinfo=None))
        self.assertEqual(updated_product.adults_price, tomorrow_group_event_2.special_price)
        self.assertEqual(updated_product.child_price, tomorrow_group_event_2.child_special_price)

        product_options = product.options.all().order_by('quantity')

        self.assertEqual(product_options.count(), 3)

        self.assertEqual(product_options[0].quantity, 0)
        self.assertEqual(product_options[1].quantity, 3)
        self.assertEqual(product_options[2].quantity, 4)

        self.assertEqual(product_options[2].total_sum, Decimal('12.00'))


    def test_create_private_product_with_options_without_booking_post(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        end_date = tomorrow + timedelta(hours=1)
        tomorrow_private_event = ExperienceEvent.objects.create(
            title='Test Private Event',
            start=tomorrow,
            end=end_date,
            total_price=Decimal('500.00'),
            calendar=self.private_calendar,
        )
        data = {
            'adults': 2,
            'children': 0,
            'language_code': 'EN',
            'customer_id': 1,
            'session_key': 'session123',
            'event_id': tomorrow_private_event.id,
            'parent_experience_id': self.private_parent_experience.id,
            'options': [
                {'id': self.option_first.id, 'quantity': 2, 'price': float(self.option_first.price)},
            ],
        }
        response = self.client.post(reverse('create-private-product-without-booking'),
                                    data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        new_product = Product.objects.first()
        self.assertEqual(new_product.start_datetime.replace(tzinfo=None), tomorrow.replace(tzinfo=None))
        self.assertEqual(new_product.total_price, Decimal('500.00'))
        self.assertEqual(new_product.adults_count, 2)

        product_options = new_product.options.all()

        self.assertEqual(product_options.count(), 1)
        self.assertEqual(product_options[0].quantity, 2)
        self.assertEqual(product_options[0].total_sum, 10.00)
