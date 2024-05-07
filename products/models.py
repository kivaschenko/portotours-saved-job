import json
import logging
import sys
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO

from PIL import Image
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import fromstr
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from geopy.geocoders import Nominatim
from schedule.models import Calendar, Event, Occurrence

geolocator = Nominatim(timeout=5, user_agent="portotours")

logger = logging.getLogger(__name__)

# Assign current user model
Customer = settings.AUTH_USER_MODEL


# ---------
# Geo Point
class MeetingPoint(models.Model):
    name = models.CharField(max_length=60, unique=True, null=False, blank=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Slug generated from name, max 255 characters")
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

    @property
    def get_map_url(self):
        if self.latitude is not None and self.longitude is not None:
            return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        return None


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


class ExperienceCategory(models.Model):
    name = models.CharField(max_length=60, unique=True, blank=True, help_text="Category name max 60 characters")
    slug = models.SlugField(max_length=60, unique=True, blank=True, help_text="Category name max 60 characters, if empty will be auto-generated from name")

    class Meta:
        ordering = ('name',)
        unique_together = ('name', 'slug')
        verbose_name_plural = 'Experience Categories'

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(ExperienceCategory, self).save(*args, **kwargs)


# -----------
# Experience

class ExperienceProvider(models.Model):
    short_name = models.CharField(max_length=60, unique=True, blank=True, help_text="Short name max 60 characters")
    slug = models.SlugField(unique=True, db_index=True, editable=True, max_length=60, blank=True,
                            help_text='Unique, max 60 characters, auto-generated from name if empty field.')
    company_name = models.CharField(max_length=255, unique=True, help_text="Company name max 255 characters")
    nif = models.CharField(max_length=60, unique=True, blank=True, null=True, help_text="National Free Identifier, max 60 characters.")
    address = models.CharField(max_length=255, blank=True, null=True, help_text="Address line max 255 characters.")
    email = models.EmailField(max_length=120, blank=True, null=True, help_text="Email address max 120 characters.")
    phone = models.CharField(max_length=60, blank=True, null=True, help_text="Phone number max 60 characters.")
    license = models.CharField(max_length=255, blank=True, null=True, help_text="License name max 255 characters.")

    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    class Meta:
        ordering = ('short_name',)

    def __str__(self):
        return self.short_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.short_name)
        super().save(*args, **kwargs)


class ParentExperience(models.Model):
    """A Parent Experience brings together all experiences with multilingual content,
    but all in one location as a geographic and destination. To save the common banner,
    card image and link between the experiences details page languages.
    """
    parent_name = models.CharField(max_length=160, unique=True, db_index=True)
    slug = models.SlugField(unique=True, db_index=True, editable=True, max_length=255, blank=True, help_text='Unique, max 255 characters.')
    banner = models.FileField(upload_to='media/banners/', null=True, blank=True)
    card_image = models.FileField(upload_to='media/cards/', null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0,
                                          help_text="Priority number using for ordering in recommendation queue")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Price for this experience: if it's private then whole total price else "
                                                                                      "- base adult price will be.")
    child_discount = models.PositiveSmallIntegerField(null=True, blank=True, default=33,
                                                      help_text="Child discount in % from price for child products")
    use_child_discount = models.BooleanField(default=True,
                                             help_text="If the children's discount percentage is included and "
                                                       "the percentage is specified, then when saving, "
                                                       "it automatically recalculates the children's price depending "
                                                       "on the main price f the amount of the discount in percent")
    child_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, null=True, blank=True, default='eur')
    price_changed_timestamp = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    use_auto_increase_old_price = models.BooleanField(default=False,
                                                      help_text="If true, the old price is automatically increased")
    increase_percentage_old_price = models.IntegerField(null=True, blank=True, default=33,
                                                        help_text="The percentage to increase old price automatically.")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True,
                                    help_text="For marketing purposes, this adult old price will be higher than the new one. If it's private - "
                                              "then old total price will be")
    child_old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True,
                                          help_text="For marketing purposes, this child old price will be higher than the new one.")
    meeting_point = models.ForeignKey(MeetingPoint, help_text="meeting point for this experience",
                                      on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name='Starting location', related_name='meeting_point')
    drop_point = models.ForeignKey(MeetingPoint, help_text="drop point for this experience", on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Drop off location', related_name='drop_points')
    pick_up_location = models.CharField(max_length=255, help_text="location to pick up this experience, max 255 characters", null=True, blank=True)
    drop_off_location = models.CharField(max_length=255, help_text="location to drop off this experience, max 255 characters", null=True, blank=True)
    max_participants = models.IntegerField(null=True, blank=True, default=8, help_text="Maximum number of participants")
    is_private = models.BooleanField(default=False, help_text="If this experience is private then to sale whole number "
                                                              "of participants as one purchase will be")
    is_exclusive = models.BooleanField(default=False, help_text="If this experience is exclusive then competition will propose.")
    is_hot_deals = models.BooleanField(default=False, help_text="If this experience is hot deals will show first queue.")
    allowed_languages = models.ManyToManyField(Language, help_text="list of languages this experience")
    categories = models.ManyToManyField(ExperienceCategory, help_text="list of categories this experience")
    free_cancellation = models.BooleanField(default=False, help_text="Free Cancellation is allowed.", null=True)
    free_cancellation_hours = models.IntegerField(null=True, blank=True, default=24, help_text="How many hours the free cancellation period from payment.")
    skip_the_line = models.BooleanField(default=False, null=True, help_text='If this experience is private then it will skip the line')
    likely_to_sell_out = models.BooleanField(default=False, null=True, help_text='If this experience is private then it will likely sell the out')
    happy_clients_number = models.IntegerField(default=0)
    recommended_by_locals = models.BooleanField(default=False, help_text="If this experience is recommended by locals", null=True)
    clean_and_safe = models.BooleanField(default=True, null=True,
                                         help_text="If this experience is clean_and_safe then the corresponding banner appears on the experience page")
    show_on_home_page = models.BooleanField(default=False, help_text="Include in the top Experiences on the home page")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=Decimal('5.0'), help_text="for example: 4.8")
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.ForeignKey(ExperienceProvider, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Provider',
                                 related_name='experience_provider', help_text='The company provider for current experience')

    def __str__(self):
        return self.parent_name

    class Meta:
        ordering = ('parent_name',)
        verbose_name_plural = 'Parent Experiences'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.parent_name)
        if self.use_auto_increase_old_price:
            self.old_price = round(self.price * Decimal(round(float(self.increase_percentage_old_price / 100 + 1), 2)), 2)
        if self.use_child_discount:
            self.child_price = round(self.price * Decimal(round(float(1 - self.child_discount / 100), 2)), 2)
            self.child_old_price = round(self.child_price * Decimal(round(float(self.increase_percentage_old_price / 100 + 1), 2)), 2)
        super().save(*args, **kwargs)


class ExperienceActiveManager(models.Manager):
    def get_queryset(self):
        return super(ExperienceActiveManager, self).get_queryset().filter(is_active=True)


class Experience(models.Model):
    """This model is both a content store and an abstraction.
    Content used for the information page of the site and abstraction as a description of the data
    for a certain event on some dates.
    So we know that this experience can happen and theoretically it can be sold on certain dates."""
    # Business logic part
    parent_experience = models.ForeignKey(ParentExperience, on_delete=models.SET_NULL,
                                          related_name='child_experiences', null=True, blank=True,
                                          help_text="The Parent Experience brings together all experiences "
                                                    "with multilingual content but same location and common banner.")
    destinations = models.ManyToManyField('destinations.Destination',
                                          help_text="may be bind to multiple destinations")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # SEO part
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=True, blank=True,
                            help_text="max 255 characters, exactly url tail that is unique")
    page_title = models.CharField(max_length=120, help_text="SEO title for header in search list, max 120 characters", null=True, blank=True)
    page_description = models.TextField(max_length=600, help_text="SEO page description, max 600 characters", null=True, blank=True)
    page_keywords = models.TextField(max_length=500, help_text="SEO keywords", null=True, blank=True)
    # Content part
    name = models.CharField(max_length=255, unique=True, help_text="Short name for the experience, max 255 characters")
    why_title = models.CharField(max_length=255, help_text="Title above why book slider, max 255 characters", null=True, blank=True)
    why_subtitle = models.CharField(max_length=500, help_text="Subtitle above why book slider, max 500 characters",
                                    null=True, blank=True)
    info_title = models.CharField(max_length=160, help_text="Info title above info block, max 160 characters", null=True, blank=True)
    info_subtitle = models.CharField(max_length=255, help_text="Info subtitle above info block, max 255 characters",
                                     blank=True, null=True)
    short_description = models.CharField(max_length=500, help_text="Short description for the preview card, max 500 characters",
                                         blank=True, null=True)
    title_description = models.CharField(max_length=255, help_text="Title for full description, max 255 characters", null=True, blank=True)
    full_description = RichTextField(max_length=6000, help_text="Full description for the Experience, max 6000 characters",
                                     null=True, blank=True)
    duration = RichTextField(max_length=60, help_text="duration of the experience, for example '5 hours'",
                             blank=True, null=True)
    accessibility = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    possibility = RichTextField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    schedule_title = models.CharField(max_length=120, help_text='Title for the schedule block in current language, max 120 characters', null=True, blank=True)
    includes_title = models.CharField(max_length=120, help_text="Title for Includes block in current language, max 120 characters", null=True, blank=True)
    includes_text = RichTextField(max_length=1000, help_text="Max 1000 characters", null=True, blank=True)
    traveler_tips_title = models.CharField(max_length=120, help_text="Title for Traveler tips block in current language, max 120 characters", null=True,
                                           blank=True)
    traveler_tips_text = RichTextField(max_length=1000, help_text="Max 1000 characters", null=True, blank=True)
    what_to_bring_title = models.CharField(max_length=120, help_text="Title for What to bring block in current language, max 120 characters", null=True,
                                           blank=True)
    what_to_bring_text = RichTextField(max_length=1000, help_text="Max 1000 characters", null=True, blank=True)
    # Recommendations block
    recommendations_title = models.CharField(max_length=255, help_text="max 255 characters", null=True, blank=True)
    recommendations_subtitle = models.CharField(max_length=500, help_text="max 500 characters", null=True, blank=True)
    experience_recommendations = models.ManyToManyField('Experience', blank=True)
    recommendations_slogan = models.CharField(max_length=160, help_text="max 160 characters, belong SEE MORE button",
                                              null=True, blank=True)
    text_above_calendar = models.CharField(max_length=60, help_text="max 60 characters, view above calendar form to hide, make blank", null=True, blank=True,
                                           default='Your dates are popular between travelers')

    objects = models.Manager()
    active = ExperienceActiveManager()

    class Meta:
        db_table = 'experiences'
        ordering = ('name',)
        unique_together = ('name', 'slug')

    def __str__(self):
        return f'{self.name} ({self.language})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.page_title:
            self.page_title = self.name
        if not self.page_description:
            self.page_description = self.short_description
        super(Experience, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:experience-detail', kwargs={'lang': self.language.code.lower(),
                                                             'slug': self.slug})

    @property
    def localized_url(self):
        return f"/experiences/{self.language.code.lower()}/{self.slug}/"

    def display_full_description(self):
        return mark_safe(self.full_description)

    def display_duration(self):
        return mark_safe(self.duration)

    def display_accessibility(self):
        return mark_safe(self.accessibility)

    def display_possibility(self):
        return mark_safe(self.possibility)

    def display_includes_text(self):
        return mark_safe(self.includes_text)

    def display_traveler_tips_text(self):
        return mark_safe(self.traveler_tips_text)

    def display_what_to_bring_text(self):
        return mark_safe(self.what_to_bring_text)

    @property
    def average_rating(self):
        # Get the related reviews for this experience
        related_reviews = self.review_set.filter(approved=True)

        # Calculate the average rating using Django's Avg aggregation function
        average_rating = related_reviews.aggregate(Avg('rating'))['rating__avg']

        # Return the average rating or None if no reviews exist
        if average_rating:
            return round(average_rating, 1)
        else:
            return None


class ExperienceEvent(Event):
    """This class inherits from Schedule Event and adds fields to define a unique price for a specific date and time. It also determines the specific
    maximum number of participants, if it differs from that specified in the Parent Experience, also determines the remaining free seats and
    how many seats have been sold.
    """
    max_participants = models.IntegerField(null=True, blank=True, help_text="Maximum number of participants, if 0 then inherit from Parent Experience.")
    booked_participants = models.IntegerField(null=True, blank=True, help_text="Already booked places.")
    remaining_participants = models.IntegerField(null=True, blank=True, help_text="Remaining participants.")
    special_price = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                        help_text="Special price if different from Parent Experience.")
    child_special_price = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                              help_text="Special child price if different from Parent Experience.")
    total_price = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, help_text="Total price for whole private tour.")

    class Meta:
        verbose_name = "Experience Event"
        verbose_name_plural = "Experience Events"

    def __str__(self):
        return "{}: {} - {}".format(
            self.title,
            self.start.strftime("%d/%m/%Y %H:%M"),
            self.end.strftime("%d/%m/%Y %H:%M"),
        )

    def save(self, *args, **kwargs):
        self.title = "{0}: {1} - {2}".format(self.calendar, self.start.strftime("%d/%m/%Y %H:%M"), self.end.strftime("%d/%m/%Y %H:%M"))
        self.color_event = "#f0500b"
        if not self.creator_id:
            self.creator_id = 1
        super().save(*args, **kwargs)

    @property
    def start_date(self):
        return self.start.strftime("%Y-%m-%d")

    @property
    def start_time(self):
        return self.start.strftime("%H:%M")

    def update_booking_data(self, booked_number, *args, **kwargs):
        self.booked_participants += booked_number
        self.remaining_participants = self.max_participants - self.booked_participants
        if self.remaining_participants < 0:
            self.remaining_participants = 0
        self.save(*args, **kwargs)


class ExperienceSchedule(models.Model):
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name="schedule")
    time = models.TimeField(null=True, blank=True)
    name_stop = models.CharField(max_length=255, null=True, blank=True, help_text="Name of stop max 255 character length.")
    description = models.TextField(max_length=600, null=True, blank=True, help_text="Description of stop max 600 characters.")

    def __str__(self):
        return f'{self.time} {self.name_stop}'

    def __repr__(self):
        return f'<ExperienceSchedule(id={self.id} time={self.time} name_stop={self.name_stop}...)>'


class ExperienceImage(models.Model):
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name='images')
    slider_image = models.FileField(upload_to='experience_images/')

    # You can add more fields if needed, like a caption or description

    def __str__(self):
        return f'Image for {self.experience.name}'

    class Meta:
        verbose_name = 'Experience Image'
        verbose_name_plural = 'Experience Images'

    def save(self, *args, **kwargs):
        if self.slider_image:
            self.resize_slider_image()
        super().save(*args, **kwargs)

    def resize_slider_image(self):
        img = Image.open(self.slider_image)
        max_width = 1090
        max_height = 600

        # Calculate the aspect ratio of the original image
        original_aspect_ratio = img.width / img.height

        # Calculate the aspect ratio of the slider
        slider_aspect_ratio = max_width / max_height

        # Resize the image to fit the width of the slider
        if original_aspect_ratio != slider_aspect_ratio:
            new_height = int(max_width / original_aspect_ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        # If the height of the resized image is greater than the slider height, crop it
        if img.height > max_height:
            excess_height = img.height - max_height
            top_crop = excess_height // 2
            bottom_crop = excess_height - top_crop
            img = img.crop((0, top_crop, img.width, img.height - bottom_crop))

        # Save the resized image to a buffer
        buffer = BytesIO()
        img.save(buffer, format='JPEG')

        # Create a new InMemoryUploadedFile instance with the resized image
        self.slider_image = InMemoryUploadedFile(
            buffer, None, f"{self.slider_image.name.split('.')[0]}_resized.jpg", 'image/jpeg',
            sys.getsizeof(buffer), None
        )


# -------
# Product

class ProductActiveManager(models.Manager):
    def get_queryset(self):
        queryset = super(ProductActiveManager, self).get_queryset()
        status_list = ['Pending', 'Payment']
        return queryset.filter(status__in=status_list)


class ProductPendingManager(models.Manager):
    def get_queryset(self):
        booking_minutes = settings.BOOKING_MINUTES
        time_limit = datetime.utcnow() - timedelta(minutes=booking_minutes)
        queryset = super(ProductPendingManager, self).get_queryset()
        return queryset.filter(status='Pending', created_at__gt=time_limit)


class ProductLostManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='Expired', customer__isnull=True, start_datetime__lt=timezone.now())


class ProductForReportManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='Payment', customer__isnull=False, reported=False)


class Product(models.Model):
    """Product - is a digital product that sells access to a specific service (Experience)
    for numbers of adults or children at a specified total price on a specified date
    and time of providing this service at a specified meeting place."""
    # Business logic
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # ID for anonymous user
    parent_experience = models.ForeignKey(ParentExperience, on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    occurrence = models.ForeignKey(Occurrence, on_delete=models.SET_NULL, null=True, blank=True)
    start_datetime = models.DateTimeField(auto_now_add=False, auto_now=False)
    end_datetime = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    adults_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0'))
    adults_count = models.IntegerField(null=True, blank=True, default=0)
    child_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0'))
    child_count = models.IntegerField(null=True, blank=True, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    expired_time = models.DateTimeField()
    status = models.CharField(max_length=30, null=True, blank=True, default='Pending',
                              choices=[
                                  ('Pending', 'Pending'),
                                  ('Expired', 'Expired'),
                                  ('Payment', 'Payment'),
                                  ('Cancelled', 'Cancelled'),
                                  ('Completed', 'Completed'),
                              ])
    random_order_number = models.CharField(max_length=30, null=True, blank=True)
    reported = models.BooleanField(default=False)
    # Stripe data
    stripe_product_id = models.CharField(max_length=220, null=True, blank=True)
    stripe_price = models.IntegerField(null=True, blank=True)  # 100 * experience.price

    objects = models.Manager()
    active = ProductActiveManager()
    pending = ProductPendingManager()
    lost_products = ProductLostManager()
    for_report = ProductForReportManager()

    def __str__(self):
        return (f"{self.parent_experience.parent_name} | {self.date_of_start}  {self.time_of_start} | "
                f"{self.total_price} {self.parent_experience.currency}")

    def __repr__(self):
        return (f"<Product(id={self.id} parent_experience_id={self.parent_experience_id} "
                f"start_datetime={self.start_datetime}...)>")

    class Meta:
        ordering = ('-created_at', '-total_price')
        get_latest_by = 'created_at'

    def save(self, *args, **kwargs):
        # recount each time during save because might be different numer of participants
        if self.adults_price and self.child_price:
            self.total_price = self._count_new_total_price()
        self.old_total_price = self._count_old_total_price()
        if self.parent_experience.is_private:
            self.stripe_product_id = (f"{self.parent_experience.parent_name.upper()} start: {self.start_datetime} language: {self.language} "
                                      f"type: private | max_participants: {self.parent_experience.max_participants}")
        else:
            self.stripe_product_id = (f"{self.parent_experience.parent_name.upper()} start: {self.start_datetime} language: {self.language} "
                                      f"type: group | participants: {self.adults_count} adults & {self.child_count} children.")
        self.stripe_price = int(self.total_price * 100)
        if self.occurrence and self.occurrence.pk is None:
            self.occurrence.save()
        if not self.created_at:
            self.created_at = timezone.now()
        if not self.expired_time:
            self.expired_time = timezone.now() + timezone.timedelta(minutes=settings.PRODUCT_EXPIRE_MINUTES)
        if not self.random_order_number:
            self.random_order_number = self.generate_random_code()
        super(Product, self).save()

    def _count_old_total_price(self):
        if not self.parent_experience.is_private:
            return self.parent_experience.old_price * self.adults_count + self.parent_experience.child_old_price * self.child_count
        else:
            return self.parent_experience.old_price

    def _count_new_total_price(self):
        return self.adults_price * self.adults_count + self.child_price * self.child_count

    @property
    def date_of_start(self):
        if not self.start_datetime:
            return ''
        return self.start_datetime.strftime('%m/%d/%Y')

    @property
    def time_of_start(self):
        if not self.start_datetime:
            return ''
        return self.start_datetime.time().strftime('%H:%M')

    @property
    def full_name(self):
        return f'{self.parent_experience.parent_name}'

    @property
    def total_booked(self):
        return self.adults_count + self.child_count

    @property
    def order_number(self):
        """
            Example usage:
            product_id = 123  # Replace this with the actual product ID
            order_number = generate_order_number(product_id)
            print("Order Number:", order_number)
            Order Number: 0000000123
        """
        # Format the product ID as a string with leading zeros to ensure it is 8 digits long
        formatted_product_id = str(self.id).zfill(6)  # Adjust the zfill value based on the length of your product IDs
        # Combine the formatted product ID with additional characters if needed
        order_number = f"ODT_PT_Booking_0000{formatted_product_id}"
        return order_number

    def generate_random_code(self):
        code = ''
        for _ in range(4):
            code += ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            code += '-'
        return code[:-1]  # Remove the last hyphen

    @property
    def free_cancellation_datetime(self):
        if self.parent_experience.free_cancellation and self.parent_experience.free_cancellation_hours:
            res = self.start_datetime - timedelta(hours=self.parent_experience.free_cancellation_hours) - timedelta(minutes=1)
            if res <= timezone.now() + timedelta(minutes=settings.PRODUCT_EXPIRE_MINUTES):
                return 0
            else:
                return res


def generate_random_code():
    """Don't touch it because issue in migrations appears too much."""
    code = ''
    for _ in range(4):
        code += ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code += '-'
    return code[:-1]  # Remove the last hyphen
