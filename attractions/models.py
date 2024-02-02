import logging
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe

from ckeditor.fields import RichTextField

from products.models import Language, ParentDestination

logger = logging.getLogger(__name__)


class ParentAttraction(models.Model):
    """A parent attraction brings together all attractions with multilingual content,
    but all in one location as a geographic and attraction. To save the common banner,
    card image and link between attraction details page languages.
    """
    parent_name = models.CharField(max_length=60, unique=True, db_index=True)
    card_image = models.FileField(upload_to='media/cards/', null=True, blank=True)
    slider_image_1 = models.FileField(upload_to='media/sliders/', null=True, blank=True)
    slider_image_2 = models.FileField(upload_to='media/sliders/', null=True, blank=True)
    slider_image_3 = models.FileField(upload_to='media/sliders/', null=True, blank=True)
    slider_image_4 = models.FileField(upload_to='media/sliders/', null=True, blank=True)
    slider_image_5 = models.FileField(upload_to='media/sliders/', null=True, blank=True)
    slider_image_6 = models.FileField(upload_to='media/sliders/', null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.parent_name

    class Meta:
        ordering = ('parent_name',)
        verbose_name = 'Parent Attraction'
        verbose_name_plural = 'Parent Attractions'


class AttractionActiveManager(models.Manager):
    def get_queryset(self):
        return super(AttractionActiveManager, self).get_queryset().filter(is_active=True)


class Attraction(models.Model):
    # Business logic part
    parent_attraction = models.ForeignKey(ParentAttraction, on_delete=models.SET_NULL,
                                          related_name='child_attractions', null=True, blank=True,
                                          help_text="The Parent Attraction brings together all attractions "
                                                    "with multilingual content but same location and common images.")
    name = models.CharField(max_length=60, help_text="max 60 characters, city name usually")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0,
                                          help_text="number for ordering in list on page by default")
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
    introduction_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    introduction_text_above_slider = RichTextField(max_length=3000, help_text="max 3000 characters", null=True,
                                                   blank=True)
    introduction_text_below_slider = RichTextField(max_length=3000, help_text="max 3000 characters", null=True,
                                                   blank=True)
    short_introduction_text = models.CharField(max_length=255, null=True, blank=True,
                                               help_text="short text for recommendation cards, max 255 characters")
    # Info block
    info_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    info_subtitle = models.CharField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    time_of_work = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    address = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    price = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    accessibility = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    possibility = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    # Recommendations block
    recommendations_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    recommendations_subtitle = models.CharField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    recommendations_slogan = models.CharField(max_length=120, help_text="max 120 characters, belong SEE MORE button",
                                              null=True, blank=True)

    objects = models.Manager()
    active = AttractionActiveManager()

    class Meta:
        ordering = ('priority_number', 'name')
        db_table = 'attractions'
        unique_together = ('name', 'slug')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Attraction(id={self.id} name={self.name} parent={self.parent_attraction} language={self.language})>"

    def get_absolute_url(self):
        return reverse("attractions:attraction-detail", kwargs={"lang": self.language, "slug": self.slug})

    @property
    def localized_url(self):
        return f"/attractions/{self.language.code.lower()}/{self.slug}/"

    def display_introduction_text_above_slider(self):
        return mark_safe(self.introduction_text_above_slider)

    def display_introduction_text_below_slider(self):
        return mark_safe(self.introduction_text_below_slider)

    def display_address(self):
        return mark_safe(self.address)

    def display_price(self):
        return mark_safe(self.price)

    def display_accessibility(self):
        return mark_safe(self.accessibility)

    def display_possibility(self):
        return mark_safe(self.possibility)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Attraction, self).save(*args, **kwargs)


class FAQAttractionManager(models.Manager):
    def get_queryset(self):
        return super(FAQAttractionManager, self).get_queryset().filter(is_active=True)


class FAQAttraction(models.Model):
    parent_attraction = models.ForeignKey(ParentAttraction, on_delete=models.SET_NULL,
                                          related_name='faq_attractions', null=True, blank=True,
                                          help_text="The Parent Attraction brings together all attractions "
                                                    "with multilingual content but same location and common FAQ.")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.CharField(max_length=255, help_text="max 255 characters")
    answer = RichTextField(max_length=3000, help_text="max 3000 characters", null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Get only active FAQ queryset by default
    objects = FAQAttractionManager()

    class Meta:
        db_table = 'faq_attractions'
        verbose_name = 'Frequently Asked Questions for Attractions'
        verbose_name_plural = 'Frequently Asked Questions for Attractions'
        ordering = ('priority_number',)

    def __str__(self):
        return self.question

    def __repr__(self):
        return (f'<FAQAttraction(id={self.id} parent_attraction={self.parent_attraction} '
                f'language={self.language} question={self.question}...)>')
