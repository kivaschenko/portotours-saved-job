from django.db import models
from django.conf import settings

from products.models import Product


class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product, blank=True)
    stripe_customer_id = models.CharField(max_length=60, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=220, null=True, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=220, null=True, blank=True)
    stripe_price = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return f'{self.stripe_checkout_session_id}'

    def __repr__(self):
        return f'<Purchase: {self.id} | {self.stripe_checkout_session_id}>'
