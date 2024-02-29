from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import User, Profile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # read_only = [
    #     'shipping_address_city',
    #     'shipping_address_country',
    #     'shipping_address_line1',
    #     'shipping_address_line2',
    #     'shipping_address_postal_code',
    #     'shipping_address_state',
    #     'shipping_address_email',
    #     'shipping_phone',
    #     'shipping_name',
    # ]
    list_display = (
        'user',
        'stripe_customer_id',
        'name',
        'phone',
        'address_city',
        'address_country',
        'address_line1',
        'address_line2',
        'address_postal_code',
        'address_state',
    )
    search_fields = ('name', 'stripe_customer_id', 'email')
    list_per_page = 10
