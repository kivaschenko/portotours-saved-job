import logging
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe

from geopy.geocoders import Nominatim
from ckeditor.fields import RichTextField

from products.models import Language

geolocator = Nominatim(timeout=5, user_agent="portotours")

logger = logging.getLogger(__name__)


class ParentDestination(models.Model):
    """A parent destination brings together all destinations with multilingual content,
    but all in one location as a geographic and destination. To save the common banner,
    card image and link between destination details page languages.
    """
    parent_name = models.CharField(max_length=60, unique=True, db_index=True)
    banner = models.FileField(upload_to='media/banners/', null=True, blank=True)
    card_image = models.FileField(upload_to='media/cards/', null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0)
    show_on_home_page = models.BooleanField(default=False, help_text="Include in the top Destinations on the home page")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.parent_name

    class Meta:
        ordering = ('parent_name',)
        verbose_name_plural = 'Parent Destinations'


class DestinationActiveManager(models.Manager):
    def get_queryset(self):
        return super(DestinationActiveManager, self).get_queryset().filter(is_active=True)


class Destination(models.Model):
    # Business logic part
    parent_destination = models.ForeignKey(ParentDestination, on_delete=models.SET_NULL,
                                           related_name='child_destinations', null=True, blank=True,
                                           help_text="The Parent destination brings together all destinations "
                                                     "with multilingual content but same location and common banner.")
    name = models.CharField(max_length=60, help_text="max 60 characters, city name usually")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # SEO part
    slug = models.SlugField(max_length=60, unique=True, db_index=True, editable=True, blank=True,
                            help_text="max 60 characters, exactly url tail that is unique")
    page_title = models.CharField(max_length=120, help_text="seo title for header in search list, max 120 characters",
                                  null=True, blank=True)
    page_description = models.TextField(max_length=600, help_text="seo page description, max 500 characters",
                                        null=True, blank=True)
    keywords = models.TextField(max_length=500, help_text="seo keywords", null=True, blank=True)
    # Content part
    main_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    main_subtitle = models.CharField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    introduction_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    introduction_subtitle = models.CharField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    introduction_text = RichTextField(max_length=6000, help_text="max 6000 characters", null=True, blank=True)
    short_introduction_text = models.CharField(max_length=255, null=True, blank=True,
                                               help_text="short text for recommendation cards, max 255 characters")
    all_about_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    when_to_visit_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    when_to_visit_text = RichTextField(max_length=6000, help_text="max 6000 characters", null=True, blank=True)
    getting_around_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    getting_around_text = RichTextField(max_length=6000, help_text="max 6000 characters", null=True, blank=True)
    travel_tips_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    travel_tips_text = RichTextField(max_length=6000, help_text="max 6000 characters", null=True, blank=True)

    top_attractions_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    top_attractions_subtitle = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    top_attractions = models.ManyToManyField('attractions.Attraction', related_name="top_attractions", blank=True)

    be_interested_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    be_interested_subtitle = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    be_interested_destinations = models.ManyToManyField('destinations.Destination', blank=True)
    # Recommendations block
    recommendations_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    recommendations_subtitle = models.CharField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    recommended_experiences = models.ManyToManyField('products.Experience', related_name='recommended', blank=True)
    recommendations_slogan = models.CharField(max_length=120, help_text="max 120 characters, belong SEE MORE button",
                                              null=True, blank=True)
    # FAQ block
    faq_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    faq_subtitle = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)

    objects = models.Manager()
    active = DestinationActiveManager()

    class Meta:
        ordering = ('name',)
        unique_together = ('name', 'slug')

    def __str__(self):
        return f'{self.name} ({self.language})'

    def get_absolute_url(self):
        return reverse('destinations:destination-detail', kwargs={'lang': self.language.code.lower(), 'slug': self.slug})

    @property
    def localized_url(self):
        return f"/destinations/{self.language.code.lower()}/{self.slug}/"

    def display_main_title(self):
        return mark_safe(self.main_title)

    def display_introduction_title(self):
        return mark_safe(self.introduction_title)

    def display_introduction_text(self):
        return mark_safe(self.introduction_text)

    def display_when_to_visit_text(self):
        return mark_safe(self.when_to_visit_text)

    def display_getting_around_text(self):
        return mark_safe(self.getting_around_text)

    def display_travel_tips_text(self):
        return mark_safe(self.travel_tips_text)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.page_title:
            self.page_title = self.name
        if not self.page_description:
            self.page_description = self.short_introduction_text
        super(Destination, self).save(*args, **kwargs)


class FAQDestinationManager(models.Manager):
    def get_queryset(self):
        return super(FAQDestinationManager, self).get_queryset().filter(is_active=True)


class FAQDestination(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True,
                                    help_text="The Parent destination brings together all destinations "
                                              "with multilingual content but same location and common FAQ.")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.CharField(max_length=255, help_text="max 255 characters")
    answer = RichTextField(max_length=3000, help_text="max 3000 characters", null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Get only active FAQ queryset by default
    objects = FAQDestinationManager()

    class Meta:
        db_table = 'faq_destination'
        verbose_name = 'Frequently Asked Questions for Destination'
        verbose_name_plural = 'Frequently Asked Questions for Destination'
        ordering = ('priority_number',)

    def __str__(self):
        return self.question

    def __repr__(self):
        return (f'<FAQDestination(id={self.id} destination={self.destination} '
                f'language={self.language} question={self.question}...)>')

    def display_answer(self):
        return mark_safe(self.answer)
