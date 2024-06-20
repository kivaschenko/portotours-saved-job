from django.contrib import admin

from .models import Purchase
from products.models import Product


class ProductInline(admin.TabularInline):
    model = Purchase.products.through
    extra = 0
    verbose_name = "Product"
    verbose_name_plural = "Products"
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("product")

    readonly_fields = (
        'product_random_order_number',
        'product_parent_experience',
        'product_total_price',
        'product_total_sum_with_options',
        'product_total_booked',
        'product_language',
        'product_date_of_start',
        'product_time_of_start',
    )
    fields = (
        'product_random_order_number',
        'product_parent_experience',
        'product_total_price',
        'product_total_sum_with_options',
        'product_total_booked',
        'product_language',
        'product_date_of_start',
        'product_time_of_start',
    )

    def product_random_order_number(self, obj):
        return obj.product.random_order_number
    product_random_order_number.short_description = "Order Number"

    def product_parent_experience(self, obj):
        return obj.product.parent_experience
    product_parent_experience.short_description = "Experience"

    def product_total_price(self, obj):
        return obj.product.total_price
    product_total_price.short_description = "Total Price"

    def product_total_sum_with_options(self, obj):
        return obj.product.total_sum_with_options
    product_total_sum_with_options.short_description = "Total Sum with Options"

    def product_date_of_start(self, instance):
        return instance.product.date_of_start
    product_date_of_start.short_description = 'Date of Start'

    def product_time_of_start(self, instance):
        return instance.product.time_of_start
    product_time_of_start.short_description = 'Time of Start'

    def product_total_booked(self, obj):
        return obj.product.total_booked
    product_total_booked.short_description = "Total Booked"

    def product_language(self, obj):
        return obj.product.language
    product_language.short_description = "Language"


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    exclude = ('stripe_customer_id', 'stripe_checkout_session_id', 'stripe_price',)
    list_filter = ('user', 'completed', 'timestamp')
    search_fields = ('stripe_payment_intent_id',)
    list_display = ('id', 'total_price', 'completed', 'timestamp', 'user', 'stripe_payment_intent_id', 'error_code')
    readonly_fields = ('total_price', 'timestamp', 'completed', 'stripe_payment_intent_id', 'user_name', 'user_email', 'user_phone', 'error_code', 'error_message')
    list_per_page = 20
    inlines = (ProductInline,)

    fieldsets = (
        (None, {
            'fields': ('user_name', 'user_email', 'user_phone', 'total_price', 'timestamp', 'completed', 'stripe_payment_intent_id', )
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def total_price(self, obj):
        if obj.stripe_price is not None:
            return float(obj.stripe_price / 100)
    total_price.short_description = 'Total price'

    def user_name(self, obj):
        return obj.user.profile.name if obj.user else ''
    user_name.short_description = 'User'

    def user_email(self, obj):
        return obj.user.email if obj.user else None
    user_email.short_description = 'User Email'

    def user_phone(self, obj):
        return obj.user.profile.phone if obj.user else None
    user_phone.short_description = 'User Phone'
