from ckeditor.fields import RichTextField
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from destinations.models import Destination
from products.models import Language, ExperienceCategory


class LandingPageActiveManager(models.Manager):
    def get_queryset(self):
        return super(LandingPageActiveManager, self).get_queryset().filter(is_active=True)


class LandingPage(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, help_text="The name of the landing page, views in main header")
    content = RichTextField(max_length=20000, blank=True, null=True, help_text="The content of the landing page, max 20 000 characters")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=True, blank=True,
                            help_text="max 255 characters, exactly url tail that is unique")
    page_title = models.CharField(max_length=255, help_text="seo title for header in search list, max 255 characters",
                                  null=True, blank=True)
    page_description = models.TextField(max_length=600, help_text="seo page description, max 500 characters",
                                        null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(ExperienceCategory, on_delete=models.SET_NULL, null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True,
                                    help_text="The destination of the landing page. "
                                              "Should be empty for parent page where all destinations are available")
    banner = models.FileField(upload_to='media/banners/', null=True, blank=True)
    card_image = models.FileField(upload_to='media/cards/', null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)
    show_in_navbar = models.BooleanField(default=False, help_text="Include in the navbar")

    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = models.Manager()
    active = LandingPageActiveManager()

    class Meta:
        ordering = ('title',)
        unique_together = ('title', 'slug')

    def __str__(self):
        return f'{self.title} ({self.language})'

    def get_absolute_url(self):
        return reverse('landing-page', kwargs={'slug': self.slug, 'lang': self.language.code.lower()})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.page_title:
            self.page_title = self.title
        super(LandingPage, self).save(*args, **kwargs)

    def display_content(self):
        return mark_safe(self.content)
