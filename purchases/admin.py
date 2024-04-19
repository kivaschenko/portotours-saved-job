from django.contrib import admin

# Register your models here.
from .models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_filter = ('user', 'completed', 'timestamp')
    search_fields = ('stripe_payment_intent_id',)
    list_display = ('id', 'total_price', 'completed', 'timestamp', 'user', 'stripe_customer_id', 'stripe_payment_intent_id')
    readonly_fields = ('user', 'products', 'timestamp', 'completed', 'stripe_customer_id',
                       'stripe_payment_intent_id', 'stripe_checkout_session_id', 'stripe_price')

    def total_price(self, obj):
        if obj.stripe_price is not None:
            return float(obj.stripe_price / 100)
    total_price.short_description = 'Total price'
