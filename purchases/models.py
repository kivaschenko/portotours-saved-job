from datetime import datetime, timedelta

from django.db import models
from django.conf import settings

from products.models import Product


class PurchaseLast24HoursManager(models.Manager):
    def get_queryset(self):
        queryset = super(PurchaseLast24HoursManager, self).get_queryset()
        now = datetime.now()
        deep_now = now - timedelta(hours=24)
        return queryset.filter(timestamp__gte=deep_now)


class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product, blank=True)
    stripe_customer_id = models.CharField(max_length=60, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=220, null=True, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=220, null=True, blank=True)
    stripe_price = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    error_code = models.CharField(max_length=100, null=True, blank=True)
    error_message = models.TextField(max_length=600, null=True, blank=True)

    objects = models.Manager()
    last24hours_manager = PurchaseLast24HoursManager()

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return f'{self.id}'

    def __repr__(self):
        return f'<Purchase: {self.id} | {self.stripe_payment_intent_id}>'

    @property
    def float_price(self):
        if self.stripe_price > 0:
            return round(self.stripe_price/100, 2)
        else:
            return 0.0
