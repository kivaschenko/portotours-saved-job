from django.contrib import admin
from django.utils.html import format_html

from .models import *  # noqa


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


@admin.register(OurValues)
class OurValuesAdmin(admin.ModelAdmin):
    list_display = ['id', 'value_title', 'display_icon']

    def display_icon(self, obj):
        if obj.icon_img:
            return format_html('<img src="{}" width="30" height="30"', obj.icon_img.url)
        else:
            return "No Icon image"
    display_icon.short_description = 'Icon image'

class OurValuesInline(admin.TabularInline):
    model = OurValues
    extra = 5


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'position', 'display_photo']

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="30" height="30"', obj.photo.url)
        else:
            return "No Photo image"

class StaffInline(admin.TabularInline):
    model = Staff
    extra = 3


@admin.register(AboutUsPage)
class AboutUsPageAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    inlines = [StaffInline, OurValuesInline]
    list_display = ['id', 'title', 'language', 'slug', 'page_title', 'updated_at']
    readonly_fields = ['updated_at']

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            formset.save()

