import sys
from io import BytesIO

from PIL import Image
from ckeditor.fields import RichTextField
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from blogs.models import Blog
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
    destinations = models.ManyToManyField(Destination, blank=True)
    banner = models.FileField(upload_to='media/banners/', null=True, blank=True,
                              help_text="Banner image, this image will be cropped and scaled max width: 1920 and max height: 460")
    card_image = models.FileField(upload_to='media/cards/', null=True, blank=True)
    priority_number = models.IntegerField('Priority', null=True, blank=True, default=0,
                                          help_text="The higher the value of the priority number, the higher it appears in the list")
    is_active = models.BooleanField(default=True)
    show_in_navbar = models.BooleanField(default=False, help_text="Include in the navbar")
    blogs_title = models.CharField('Featured Articles Title', max_length=255, help_text="Title above Featured Articles section, max 255 characters",
                                   blank=True, null=True)
    blogs = models.ManyToManyField(Blog, blank=True)
    title_related_landing_pages = models.CharField(max_length=255, blank=True, null=True, help_text="Title of the landing page, max 255 characters", )
    related_landing_pages = models.ManyToManyField('LandingPage', blank=True)
    # FAQ block
    faq_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    faq_subtitle = models.CharField(max_length=255, help_text="max 255 characters", null=True, blank=True)


    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = models.Manager()
    active = LandingPageActiveManager()

    class Meta:
        ordering = ('-priority_number', 'title')
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
        if self.banner:
            self.resize_banner()
        super().save(*args, **kwargs)

    def display_content(self):
        return mark_safe(self.content)

    def resize_banner(self):
        img = Image.open(self.banner)
        max_width = 1920
        max_height = 460
        original_aspect_ratio = img.width / img.height
        banner_aspect_ratio = max_width / max_height
        if original_aspect_ratio != banner_aspect_ratio:
            new_height = int(max_width / original_aspect_ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        if img.height > max_height:
            excess_height = img.height - max_height
            top_crop = excess_height // 2
            bottom_crop = excess_height - top_crop
            img = img.crop((0, top_crop, img.width, img.height - bottom_crop))
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        self.banner = InMemoryUploadedFile(buffer, None, f"{self.banner.name.split('.')[0]}_resized.jpg", 'image/jpeg',
                                           sys.getsizeof(buffer), None)


class FAQLandingPageManager(models.Manager):
    def get_queryset(self):
        return super(FAQLandingPageManager, self).get_queryset().filter(is_active=True)


class FAQLandingPage(models.Model):
    landing_page = models.ForeignKey(LandingPage, on_delete=models.SET_NULL, null=True, blank=True, related_name='faq_landing_list')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.CharField(max_length=255, help_text="max 255 characters")
    answer = RichTextField(max_length=3000, help_text="max 3000 characters", null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Get only active FAQ queryset by default
    objects = FAQLandingPageManager()

    class Meta:
        db_table = 'faq_landing_page'
        verbose_name = 'Frequently Asked Questions for Landing Page'
        verbose_name_plural = 'Frequently Asked Questions for Landing Page'
        ordering = ('-priority_number',)

    def __str__(self):
        return self.question

    def __repr__(self):
        return (f'<FAQLandingPage(id={self.id} landing_page={self.landing_page} '
                f'language={self.language} question={self.question}...)>')

    def display_answer(self):
        return mark_safe(self.answer)
