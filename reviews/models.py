from django.db import models
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags

from accounts.models import Profile
from products.models import ParentExperience, Experience


class Review(models.Model):
    experience = models.ForeignKey(Experience, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    short_text = models.TextField(max_length=500, null=True, blank=False)
    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=False, auto_now=False)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.id} - about {self.experience}'

    def __repr__(self):
        return f'<Review(id={self.id} profile={self.profile} experience={self.experience}...)>'


class Testimonial(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    short_text = models.TextField(max_length=320, help_text="max 320 characters", null=True, blank=True)
    show_on_home_page = models.BooleanField(default=True, help_text="Include in the top Reviews on the home page")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at', )

    def __str__(self):
        return f'{self.id} - {self.profile}'

    def __repr__(self):
        return f'<Testimonial(id={self.id} profile={self.profile})>'
