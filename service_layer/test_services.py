import unittest
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.core import mail
from django.test import TestCase

from service_layer.services import (
    update_purchase_and_send_email_payment_intent_failed,
    update_purchase_by_payment_intent_id,
    create_new_stripe_customer_id,
    set_real_user_in_purchase
)
from service_layer.events import (
    StripePaymentIntentFailed,
    StripePaymentIntentSucceeded,
    StripeChargeSucceeded,
    StripeCustomerCreated
)
from service_layer.bus_messages import handle


class TestUpdatePurchaseAndSendEmailPaymentIntentFailed(TestCase):

    @patch('service_layer.services.send_mail')
    @patch('service_layer.services.Purchase')  # Mock the Purchase model to avoid database interactions
    def test_update_purchase_and_send_email(self, mock_purchase, mock_send_mail):
        # Arrange
        mock_purchase_instance = MagicMock()
        mock_purchase.objects.get.return_value = mock_purchase_instance
        mock_purchase_instance.id = 100
        mock_purchase_instance.products.all.return_value.exists.return_value = True
        mock_purchase_instance.products.all.return_value = [
            MagicMock(random_order_number='16G6-4AZQ-9WFN-XGAV', full_name='Sunset, Fado and Tapas Walking Tour', total_booked=5, language='English', total_price=229.95),
            MagicMock(random_order_number='W6MQ-6IHO-JYVY-VILR', full_name='Wine Experience at José Maria da Fonseca parent', total_booked=5, language='English', total_price=399.99)
        ]

        payment_intent_id = 'test_payment_intent_id'
        stripe_customer_id = 'test_stripe_customer_id'
        error_code = 'card_declined'
        error_message = 'Your card was declined.'
        name = 'Ben Afflec'
        email = 'teodorathome@yahoo.com'
        phone = '+12124656000'

        # Act
        update_purchase_and_send_email_payment_intent_failed(
            payment_intent_id=payment_intent_id,
            stripe_customer_id=stripe_customer_id,
            error_code=error_code,
            error_message=error_message,
            name=name,
            email=email,
            phone=phone
        )

        # Assert
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args[1]
        expected_message = (
            "Purchase Id: 100\n\n"
            "\nOrder ID: 16G6-4AZQ-9WFN-XGAV\n"
            "\tProduct name: Sunset, Fado and Tapas Walking Tour\n"
            "\tNumber of passengers: 5\n"
            "\tLanguage: English\n"
            "\tTotal sum: €229.95\n\n"
            "\nOrder ID: W6MQ-6IHO-JYVY-VILR\n"
            "\tProduct name: Wine Experience at José Maria da Fonseca parent\n"
            "\tNumber of passengers: 5\n"
            "\tLanguage: English\n"
            "\tTotal sum: €399.99\n\n"
            "\nClient info:\n"
            "\tStripe ID: test_stripe_customer_id\n"
            "\tName: Ben Afflec\n"
            "\tEmail: teodorathome@yahoo.com\n"
            "\tPhone: +12124656000\n\n"
            "\nError info:\n"
            "\tError code: card_declined\n"
            "\tError message: Your card was declined.\n"
        )

        self.assertEqual(call_args['subject'], 'Unsuccessful attempt of payment for order(s): 16G6-4AZQ-9WFN-XGAV, W6MQ-6IHO-JYVY-VILR')
        self.assertEqual(call_args['message'], expected_message)
        self.assertEqual(call_args['from_email'], settings.ORDER_EMAIL)
        self.assertEqual(call_args['recipient_list'], [settings.ADMIN_EMAIL, settings.MANAGER_EMAIL])


class TestEventHandlers(TestCase):

    @patch('service_layer.bus_messages.handle_stripe_charge_success')
    def test_handle_stripe_charge_succeeded(self, mock_handler):
        event = StripeChargeSucceeded(
            payment_intent_id='pi_123',
            name='John Doe',
            email='john@example.com',
            phone='1234567890',
            address_city='City',
            address_country='Country',
            address_line1='123 Street',
            address_line2='Apt 1',
            address_postal_code='12345',
            address_state='State'
        )
        handle(event)
        mock_handler.assert_called_once_with(event)

    @patch('service_layer.services.update_purchase_by_payment_intent_id')
    def test_handle_stripe_payment_intent_succeeded(self, mock_handler):
        event = StripePaymentIntentSucceeded(payment_intent_id='pi_123')
        handle(event)
        mock_handler.assert_called_once_with(payment_intent_id='pi_123')

    @patch('service_layer.services.update_purchase_and_send_email_payment_intent_failed')
    def test_handle_stripe_payment_intent_failed(self, mock_handler):
        event = StripePaymentIntentFailed(
            payment_intent_id='pi_123',
            stripe_customer_id='cus_123',
            error_code='card_declined',
            error_message='Card was declined',
            name='John Doe',
            email='john@example.com',
            phone='1234567890',
            address_city='City',
            address_country='Country',
            address_line1='123 Street',
            address_line2='Apt 1',
            address_postal_code='12345',
            address_state='State'
        )
        handle(event)
        mock_handler.assert_called_once_with(event)

    @patch('service_layer.services.create_profile_and_generate_password')
    def test_handle_stripe_customer_created(self, mock_handler):
        event = StripeCustomerCreated(
            stripe_customer_id='cus_123',
            name='John Doe',
            email='john@example.com',
            phone='1234567890',
            address_city='City',
            address_country='Country',
            address_line1='123 Street',
            address_line2='Apt 1',
            address_postal_code='12345',
            address_state='State'
        )
        handle(event)
        mock_handler.assert_called_once_with(event)


class TestServiceFunctions(TestCase):

    @patch('service_layer.services.Purchase')
    def test_update_purchase_by_payment_intent_id(self, mock_purchase):
        mock_purchase_instance = MagicMock()
        mock_purchase.objects.filter().first.return_value = mock_purchase_instance

        update_purchase_by_payment_intent_id(payment_intent_id='pi_123', customer_id='cus_123')

        mock_purchase_instance.save.assert_called()
        self.assertEqual(mock_purchase_instance.completed, True)
        self.assertEqual(mock_purchase_instance.stripe_customer_id, 'cus_123')

    @patch('service_layer.services.stripe.Customer.create')
    def test_create_new_stripe_customer_id(self, mock_stripe_customer_create):
        mock_customer = MagicMock(id='cus_123')
        mock_stripe_customer_create.return_value = mock_customer

        customer = create_new_stripe_customer_id(
            name='John Doe',
            email='john@example.com',
            phone='1234567890',
            address_city='City',
            address_country='Country',
            address_line1='123 Street',
            address_line2='Apt 1',
            address_postal_code='12345',
            address_state='State'
        )

        self.assertEqual(customer.id, 'cus_123')
        mock_stripe_customer_create.assert_called_once()


class TestSetRealUserInPurchase(TestCase):

    @patch('service_layer.services.Profile')
    @patch('service_layer.services.Purchase')
    def test_set_real_user_in_purchase(self, mock_purchase, mock_profile):
        mock_profile_instance = MagicMock(user=MagicMock(id=1))
        mock_profile.objects.get.return_value = mock_profile_instance
        mock_purchase_instance = MagicMock(user_id=1)
        mock_purchase.last24hours_manager.filter.return_value = [mock_purchase_instance]

        set_real_user_in_purchase(payment_intent_id='pi_123', customer_id='cus_123')

        mock_purchase_instance.save.assert_called()
        mock_profile.objects.get.assert_called_once_with(stripe_customer_id='cus_123')


if __name__ == '__main__':
    unittest.main()
