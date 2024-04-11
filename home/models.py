from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags

from ckeditor.fields import RichTextField


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Page(models.Model):
    title = models.CharField(max_length=60, unique=True, help_text="Title of the page")
    slug = models.SlugField(unique=True, help_text="Slug of the page, if blank, will be generated automatically from the title, max 255 characters",
                            max_length=255, null=True, blank=True)
    content = RichTextField(max_length=20000, help_text="markdown content of the page, max 20 000 characters", blank=True, null=True)
    page_title = models.CharField(max_length=60, help_text="seo title for header in search list, max 120 characters",
                                  null=True, blank=True)
    page_description = models.TextField(max_length=600, help_text="seo page description, max 500 characters",
                                        null=True, blank=True)
    keywords = models.TextField(max_length=500, help_text="seo keywords", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title

    def absolute_url(self):
        return reverse('pages/en/', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.page_title:
            self.page_title = self.title
        if not self.page_description:
            self.page_description = strip_tags(self.content)[:200]
        super(Page, self).save(*args, **kwargs)

    def display_content(self):
        return mark_safe(self.content)
