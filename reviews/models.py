from django.db import models
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags

from ckeditor.fields import RichTextField

from accounts.models import Profile
from products.models import ParentExperience


class Review(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    parent_experience = models.ForeignKey(ParentExperience, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    short_text = models.CharField(max_length=255, null=True, blank=True)
    text = RichTextField(max_length=6000, help_text="max 6000 characters", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=False, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', '-rating',)
        unique_together = ('profile', 'parent_experience')

    def __str__(self):
        return f'{self.id} - about {self.parent_experience} from {self.profile}'

    def __repr__(self):
        return f'<Review(id={self.id} profile={self.profile} parent_experience={self.parent_experience}...)>'

    def display_text(self):
        return mark_safe(self.text)

    def save(self, *args, **kwargs):
        if not self.short_text:
            self.short_text = strip_tags(self.text)[:255]
        super(Review, self).save(*args, **kwargs)
