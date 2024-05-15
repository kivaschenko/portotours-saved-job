import unittest
from unittest.mock import patch, MagicMock

from django.conf import settings
from service_layer.services import update_purchase_and_send_email_payment_intent_failed

from django.core import mail
from django.test import TestCase


class EmailTest(TestCase):
    def test_update_purchase_and_send_email_payment_intent_failed(self):
        # Call your function with test data
        update_purchase_and_send_email_payment_intent_failed(
            payment_intent_id='test_intent_id',
            stripe_customer_id='test_customer_id',
            error_code='card_declined',
            error_message='Your card was declined.',
            name='Ben Affleck',
            email='ben@example.com',
            phone='+12124656000'
        )

        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)

        # Check the subject of the email
        self.assertEqual(mail.outbox[0].subject, 'New Order payment failed: test_intent_id, card_declined')

        # Check the email body content
        expected_body_content = [
            # "Order ID:", "Product name:", "Number of passengers:", "Language:", "Total sum:",
            "Client info:", "Stripe ID:", "Name:", "Email:", "Phone:",
            "Error info:", "Error code: card_declined", "Error message: Your card was declined."
        ]
        for content in expected_body_content:
            self.assertIn(content, mail.outbox[0].body)


class TestUpdatePurchaseAndSendEmail(TestCase):

    @patch('service_layer.services.send_mail')
    @patch('service_layer.services.Purchase')  # Mock the Purchase model to avoid database interactions
    def test_update_purchase_and_send_email(self, mock_purchase, mock_send_mail):
        # Arrange
        mock_purchase_instance = MagicMock()
        mock_purchase.objects.get.return_value = mock_purchase_instance
        mock_purchase_instance.products.all.return_value.exists.return_value = True
        mock_purchase_instance.products.all.return_value = [
            MagicMock(random_order_number='16G6-4AZQ-9WFN-XGAV', full_name='Sunset, Fado and Tapas Walking Tour', total_booked=5, language='English',
                      total_price=229.95),
            MagicMock(random_order_number='W6MQ-6IHO-JYVY-VILR', full_name='Wine Experience at José Maria da Fonseca parent', total_booked=5,
                      language='English', total_price=399.99)
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
            "\nOrder ID: 16G6-4AZQ-9WFN-XGAV\n"
            "\tProduct name: Sunset, Fado and Tapas Walking Tour\n"
            "\tNumber of passengers: 5\n"
            "\tLanguage: English\n"
            "\tTotal sum: 229.95\n\n"
            "\nOrder ID: W6MQ-6IHO-JYVY-VILR\n"
            "\tProduct name: Wine Experience at José Maria da Fonseca parent\n"
            "\tNumber of passengers: 5\n"
            "\tLanguage: English\n"
            "\tTotal sum: 399.99\n\n"
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


# if __name__ == '__main__':
#     unittest.main()
