from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from products.models import Product, ParentExperience, Language


class ProductDiscountAggregationTests(TestCase):

    def setUp(self):
        self.session_key = 'test_session_key'

        # Create a language instance
        self.language = Language.objects.create(code='EN', name='English')

        # Create a parent experience instance (private)
        self.private_experience = ParentExperience.objects.create(
            parent_name='Private Experience',
            price=Decimal('200.00'),
            second_purchase_discount=Decimal('20.00'),
            is_private=True
        )

        # Create a parent experience instance (non-private)
        self.non_private_experience = ParentExperience.objects.create(
            parent_name='Non-Private Experience',
            price=Decimal('100.00'),
            second_purchase_discount=Decimal('10.00'),
            is_private=False
        )

    def create_product(self, parent_experience, adults_count=1, price_is_special=True):
        return Product.objects.create(
            customer=None,
            session_key=self.session_key,
            parent_experience=parent_experience,
            language=self.language,
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timezone.timedelta(hours=1),
            adults_price=parent_experience.price,
            adults_count=adults_count,
            total_price=parent_experience.price * adults_count,
            price_is_special=price_is_special,
            status='Pending'
        )

    def test_private_product_discount(self):
        # Create private product
        self.create_product(self.private_experience)

        # Aggregate discounts
        total_discount = Product.aggregate_total_second_discount(self.session_key)

        # Expect the discount to be equal to the second_purchase_discount of the private experience
        self.assertEqual(total_discount, Decimal('20.00'))

    def test_non_private_product_discount(self):
        # Create non-private product with 3 adults
        self.create_product(self.non_private_experience, adults_count=3)

        # Aggregate discounts
        total_discount = Product.aggregate_total_second_discount(self.session_key)

        # Expect the discount to be second_purchase_discount * adults_count
        self.assertEqual(total_discount, Decimal('30.00'))

    def test_mixed_product_discounts(self):
        # Create private and non-private products
        self.create_product(self.private_experience)
        self.create_product(self.non_private_experience, adults_count=2)

        # Aggregate discounts
        total_discount = Product.aggregate_total_second_discount(self.session_key)

        # Expect the total discount to be the sum of private and non-private discounts
        expected_discount = Decimal('20.00') + Decimal('20.00')  # 20 from private, 10*2 from non-private
        self.assertEqual(total_discount, expected_discount)

    def test_no_discount_if_not_special(self):
        # Create non-private product with price_is_special=False
        self.create_product(self.non_private_experience, adults_count=2, price_is_special=False)

        # Aggregate discounts
        total_discount = Product.aggregate_total_second_discount(self.session_key)

        # Expect no discount
        self.assertEqual(total_discount, Decimal('0.00'))
