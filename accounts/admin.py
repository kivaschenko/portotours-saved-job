from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

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
    list_display = ("id", "email", "first_name", "last_name", "is_staff", "profile")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'stripe_customer_id',
        'display_avatar',
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
    list_per_page = 20
    readonly_fields = (
        'user',
        'stripe_customer_id',
        'name',
        'email',
        'phone',
        'address_city',
        'address_country',
        'address_line1',
        'address_line2',
        'address_postal_code',
        'address_state',
    )

    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;">', obj.avatar.url)
        else:
            return "No Avatar"

    display_avatar.short_description = "Avatar"
