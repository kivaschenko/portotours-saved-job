from django.contrib import admin

from .models import Subscriber

admin.site.register(Subscriber)


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at']
    search_fields = ['email', ]
