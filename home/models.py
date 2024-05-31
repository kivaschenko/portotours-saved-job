from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags

from ckeditor.fields import RichTextField
from products.models import Language

from home.fields import SVGAndImageField

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Page(models.Model):
    title = models.CharField(max_length=60, unique=True, help_text="Title of the page")
    slug = models.SlugField(unique=True, help_text="Slug of the page, if blank, will be generated automatically from the title, max 255 characters",
                            max_length=255, null=True, blank=True)
    content = RichTextField(max_length=50000, help_text="markdown content of the page, max 50 000 characters", blank=True, null=True)
    page_title = models.CharField(max_length=60, help_text="SEO title for header in search list, max 120 characters",
                                  null=True, blank=True)
    page_description = models.TextField(max_length=600, help_text="SEO page description, max 500 characters",
                                        null=True, blank=True)
    keywords = models.TextField(max_length=500, help_text="SEO keywords", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page_detail', kwargs={'slug': self.slug})

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


class AboutUsPage(models.Model):
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    main_image_desktop = models.ImageField(upload_to="about_us/", null=True, blank=True)
    main_image_mobile = models.ImageField(upload_to="about_us/", null=True, blank=True)
    title = models.CharField(max_length=120, unique=True, help_text="Title of the page, max 120 characters, for example 'About Us' text", )
    intro_text = models.TextField(max_length=1000, help_text="Under title text block markdown content of the page, max 1000 characters", blank=True, null=True)
    our_mission_title = models.CharField(max_length=120, help_text="max 120 characters", blank=True, null=True)
    our_mission_text = models.TextField(max_length=1000, help_text="Under Our Mission title text block markdown content of the page, max 1000 characters",
                                        blank=True, null=True)
    our_values_title = models.CharField(max_length=120, help_text="max 120 characters", blank=True, null=True)
    our_team_title = models.CharField(max_length=120, help_text="max 120 characters", blank=True, null=True)
    our_team_text = models.TextField(max_length=1000, help_text="max 1000 characters", blank=True, null=True)
    # SEO
    slug = models.SlugField(unique=True, help_text="Slug of the page, if blank, will be generated automatically from the title, max 255 characters",
                            max_length=255, null=True, blank=True)
    page_title = models.CharField(max_length=60, help_text="SEO title for header in search list, max 120 characters", null=True, blank=True)
    page_description = models.TextField(max_length=600, help_text="SEO page description, max 500 characters", null=True, blank=True)
    keywords = models.TextField(max_length=500, help_text="SEO keywords", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return f'{self.title} ({self.language})'

    def get_absolute_url(self):
        return reverse('about-us', kwargs={'lang': self.language.code.lower(), 'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.page_title:
            self.page_title = self.title
        if not self.page_description:
            self.page_description = strip_tags(self.intro_text)[:200]
        super(AboutUsPage, self).save(*args, **kwargs)


class OurValues(models.Model):
    about_us_page = models.ForeignKey(AboutUsPage, on_delete=models.SET_NULL, null=True, blank=True, related_name='our_values')
    icon_img = models.FileField(upload_to='about_us/icons/', null=True, blank=True)
    value_title = models.CharField(max_length=120, help_text="max 120 characters", unique=True)
    value_text = models.TextField(max_length=1000, help_text="max 1000 characters", )

    class Meta:
        verbose_name_plural = 'our values'

    def __str__(self):
        return self.value_title

    def __repr__(self):
        return f"<OurValues {self.value_title}>"


class Staff(models.Model):
    about_us_page = models.ForeignKey(AboutUsPage, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')
    full_name = models.CharField(max_length=120, help_text="Full name of the staff member", unique=True)
    position = models.CharField(max_length=120, help_text="Position of the staff member")
    description = models.TextField(max_length=1000, help_text="Description of the staff member", null=True, blank=True)
    photo = models.ImageField(upload_to='about_us/staff_photos/', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'staff'

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"<Staff {self.full_name}>"
