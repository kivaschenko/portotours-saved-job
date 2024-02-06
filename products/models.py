import json
import logging
from django.contrib.gis.geos import fromstr
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from geopy.geocoders import Nominatim
from ckeditor.fields import RichTextField

geolocator = Nominatim(timeout=5, user_agent="portotours")

logger = logging.getLogger(__name__)


# ---------
# Geo Point
class MeetingPoint(models.Model):
    name = models.CharField(max_length=60, unique=True, null=False, blank=False)
    slug = models.SlugField(max_length=70, unique=True, blank=True, help_text="Slug generated from name")
    country = models.CharField(max_length=150, blank=True, default='Portugal',
                               help_text="Country name max 150 characters")
    region = models.CharField(max_length=150, blank=True, help_text="Region name max 150 characters", null=True)
    city = models.CharField(max_length=150, blank=True, help_text="City name max 150 characters", null=True)
    address = models.CharField(max_length=255, blank=True, help_text="Address name max 255 characters", null=True)
    auto_location = models.BooleanField(default=True, null=False,
                                        help_text="After saving coordinates will be auto-defined by address", )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    update_coords_by_geom = models.BooleanField(default=False, null=False,
                                                help_text="Automatically update longitude and latitude from map "
                                                          "marker place. Turn off Auto location for this.")
    auto_update_address_name = models.BooleanField(default=True, null=False,
                                                   help_text="Automatically update address name form open street maps "
                                                             "response by coordinates.")
    geom = gis_models.PointField(srid=4326, blank=True, null=True,
                                 help_text="If the cursor was moved, then the coordinates (longitude, latitude) "
                                           "will be changed automatically after saving. Auto Location must be off.")
    location_raw = models.JSONField(blank=True, null=True, help_text="Raw describe from open street maps coordinates.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.auto_location:
            current_location = self.get_geolocation()
            if current_location is None:
                logger.error(f"Could not get geolocation for {self.name} with address: {self.address}")
                pass
            else:
                self.latitude = current_location.latitude
                self.longitude = current_location.longitude
                self.geom = fromstr(f"POINT({self.longitude} {self.latitude})", srid=4326)
                logger.info(f"Got geolocation for {self.name} with address: {self.address}")
                self.location_raw = json.dumps(current_location.raw)
        else:
            if self.update_coords_by_geom:
                self.latitude = self.geom.y
                self.longitude = self.geom.x
                logger.info(f"Got geolocation for {self.name} with geom marker: {self.geom.x}, {self.geom.y}")
        super(MeetingPoint, self).save(*args, **kwargs)
        if self.auto_update_address_name:
            self.address = self.reverse_geolocation()
        super(MeetingPoint, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<MeetingPoint(name={self.name}, slug={self} country={self.country}, region={self.region}...)>"

    def get_absolute_url(self):
        return reverse('products:meeting_point', kwargs={'slug': self.slug})

    def get_geolocation(self):
        if not self.address:
            return None
        match_stmt = f"{self.address}"
        location = geolocator.geocode(match_stmt)
        return location

    def reverse_geolocation(self):
        location = geolocator.reverse(f"{self.latitude}, {self.longitude}")
        return location.address


# --------
# Language
class LanguageActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Language(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=60)
    is_active = models.BooleanField(default=True)

    active = LanguageActiveManager()
    objects = models.Manager()

    class Meta:
        ordering = ('name',)
        unique_together = ('code', 'name')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Language(id={self.id}, name={self.name})>"


# -----------
# Experience

class ParentExperience(models.Model):
    """A Parent Experience brings together all experiences with multilingual content,
    but all in one location as a geographic and destination. To save the common banner,
    card image and link between the experiences details page languages.
    """
    parent_name = models.CharField(max_length=60, unique=True, db_index=True)
    banner = models.FileField(upload_to='media/banners/', null=True, blank=True)
    card_image = models.FileField(upload_to='media/cards/', null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.parent_name

    class Meta:
        ordering = ('parent_name',)
        verbose_name_plural = 'Parent Experiences'


class ExperienceActiveManager(models.Manager):
    def get_queryset(self):
        return super(ExperienceActiveManager, self).get_queryset().filter(is_active=True)


class Experience(models.Model):
    # Business logic part
    parent_experience = models.ForeignKey(ParentExperience, on_delete=models.SET_NULL,
                                          related_name='child_experiences', null=True, blank=True,
                                          help_text="The Parent Experience brings together all experiences "
                                                    "with multilingual content but same location and common banner.")
    destinations = models.ManyToManyField('destinations.Destination',
                                          help_text="may be bind to multiple destinations")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    meeting_point = models.ForeignKey(MeetingPoint, help_text="meeting point for this experience",
                                      on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # SEO part
    slug = models.SlugField(max_length=60, unique=True, db_index=True, editable=True, blank=True,
                            help_text="max 60 characters, exactly url tail that is unique")
    page_title = models.CharField(max_length=120, help_text="seo title for header in search list, max 120 characters",
                                  null=True, blank=True)
    page_description = models.TextField(max_length=600, help_text="seo page description, max 500 characters",
                                        null=True, blank=True)
    page_keywords = models.TextField(max_length=500, help_text="seo keywords", null=True, blank=True)
    # Content part
    name = models.CharField(max_length=60, unique=True,
                            help_text="Short name for the experience, max 60 characters")
    title_for_booking_form = models.CharField(max_length=120, help_text="Title above book form, max 120 characters",
                                              null=True, blank=True)
    long_name = models.CharField(max_length=255, help_text="Long name for the experience, max 255 characters",
                                 blank=True, null=True)
    short_description = models.CharField(max_length=255,
                                         help_text="Short description for the Short Name, max 255 characters",
                                         blank=True, null=True)
    full_description = RichTextField(max_length=6000,
                                     help_text="Full description for the Experience, max 6000 characters",
                                     null=True, blank=True)
    languages = RichTextField(help_text="list of available languages during experience trip", null=True, blank=True)
    duration = RichTextField(max_length=60, help_text="duration of the experience, for example '5 hours'",
                             blank=True, null=True)
    accessibility = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    possibility = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    # Recommendations block
    recommendations_title = models.CharField(max_length=120, help_text="max 120 characters", null=True, blank=True)
    recommendations_subtitle = models.CharField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    recommendations_slogan = models.CharField(max_length=120, help_text="max 120 characters, belong SEE MORE button",
                                              null=True, blank=True)

    objects = models.Manager()
    active = ExperienceActiveManager()

    class Meta:
        db_table = 'experiences'
        ordering = ('name',)
        unique_together = ('name', 'slug')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Experience, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:experience-detail', kwargs={'lang': self.language.code.lower(),
                                                             'slug': self.slug})

    @property
    def localized_url(self):
        return f"/experienceVjs/{self.language.code.lower()}/{self.slug}/"

    def display_full_description(self):
        return mark_safe(self.full_description)

    def display_languages(self):
        return mark_safe(self.languages)

    def display_duration(self):
        return mark_safe(self.duration)

    def display_accessibility(self):
        return mark_safe(self.accessibility)

    def display_possibility(self):
        return mark_safe(self.possibility)
