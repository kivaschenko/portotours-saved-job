from django.contrib import admin

from .models import Subscriber, Page


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'subscribed_at']
    readonly_fields = ['subscribed_at']
    search_fields = ['email', ]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'page_title', 'updated_at']
    readonly_fields = ['updated_at']
    search_fields = ['title']
