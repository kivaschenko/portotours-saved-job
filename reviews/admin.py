from django.contrib import admin

from reviews.models import Review, Testimonial


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'experience', 'rating', 'short_text', 'approved', 'created_at']
    list_filter = ['approved', 'created_at', 'experience']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile', 'short_text', 'updated_at']
