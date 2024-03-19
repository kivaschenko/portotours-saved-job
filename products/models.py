import json
import logging
from decimal import Decimal
from datetime import datetime, timedelta

from django.contrib.gis.geos import fromstr
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.conf import settings

from geopy.geocoders import Nominatim
from ckeditor.fields import RichTextField
from schedule.models import Calendar, Event, Occurrence

geolocator = Nominatim(timeout=5, user_agent="portotours")

logger = logging.getLogger(__name__)

# Assign current user model
Customer = settings.AUTH_USER_MODEL


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
    parent_name = models.CharField(max_length=160, unique=True, db_index=True)
    slug = models.SlugField(unique=True, db_index=True, editable=True, max_length=200, blank=True)
    banner = models.FileField(upload_to='media/banners/', null=True, blank=True)
    card_image = models.FileField(upload_to='media/cards/', null=True, blank=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0,
                                          help_text="Priority number using for ordering in recommendation queue")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
                                    help_text="For marketing purposes, this adult old price will be higher than the new one.")
    child_old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True,
                                          help_text="For marketing purposes, this child old price will be higher than the new one.")
    meeting_point = models.ForeignKey(MeetingPoint, help_text="meeting point for this experience",
                                      on_delete=models.SET_NULL, null=True, blank=True)
    max_participants = models.IntegerField(null=True, blank=True, default=8, help_text="Maximum number of participants")
    is_private = models.BooleanField(default=False, help_text="If this experience is private then to sale whole number "
                                                              "of participants as one purchase will be")
    allowed_languages = models.ManyToManyField(Language, help_text="list of languages this experience")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.parent_name

    class Meta:
        ordering = ('parent_name',)
        verbose_name_plural = 'Parent Experiences'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.parent_name)
        if self.use_auto_increase_old_price:
            self.old_price = self.price * Decimal(round(float(self.increase_percentage_old_price / 100 + 1), 2))
        if self.use_child_discount:
            self.child_price = self.price * Decimal(round(float(1 - self.child_discount / 100), 2))
            self.child_old_price = self.child_price * Decimal(round(float(self.increase_percentage_old_price / 100 + 1), 2))
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
        return f"/experiences/{self.language.code.lower()}/{self.slug}/"

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
        self.save(*args, **kwargs)
    

# -------
# Product

class ProductActiveManager(models.Manager):
    def get_queryset(self):
        queryset = super(ProductActiveManager, self).get_queryset()
        status_list = ['Pending', 'Processing', 'Payment']
        return queryset.filter(status__in=status_list)


class ProductPendingManager(models.Manager):
    def get_queryset(self):
        queryset = super(ProductPendingManager, self).get_queryset()
        return queryset.filter(status='Pending')


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
    expired_time = models.DateTimeField()
    status = models.CharField(max_length=30, null=True, blank=True, default='Pending',
                              choices=[
                                  ('Pending', 'Pending'),
                                  ('Cancelled', 'Cancelled'),
                                  ('Expired', 'Expired'),
                                  ('Processing', 'Processing'),
                                  ('Payment', 'Payment'),
                                  ('Completed', 'Completed'),
                              ])
    # Stripe data
    stripe_product_id = models.CharField(max_length=220, null=True, blank=True)
    stripe_price = models.IntegerField(null=True, blank=True)  # 100 * experience.price

    objects = models.Manager()
    active = ProductActiveManager()
    pending = ProductPendingManager()

    def __str__(self):
        return (f"{self.parent_experience.parent_name} | {self.date_of_start}  {self.time_of_start} | "
                f"{self.total_price} {self.parent_experience.currency}")

    def __repr__(self):
        return (f"<Product(id={self.id} parent_experience_id={self.parent_experience_id} "
                f"start_datetime={self.start_datetime}...)>")

    class Meta:
        ordering = ('-created_at', '-total_price')

    def save(self, *args, **kwargs):
        # recount each time during save because might be different numer of participants
        self.total_price = self._count_new_total_price()
        self.old_total_price = self._count_old_total_price()
        self.stripe_product_id = (f"{self.parent_experience.parent_name.upper()} start: {self.start_datetime} language: {self.language} "
                                  f"participants: {self.adults_count} adults & {self.child_count} children.")
        self.stripe_price = int(self.total_price * 100)
        if not self.expired_time:
            self.expired_time = datetime.utcnow() + timedelta(minutes=settings.BOOKING_MINUTES)  # by default 30 minutes
        super(Product, self).save()

    def _count_old_total_price(self):
        return self.parent_experience.old_price * self.adults_count + self.parent_experience.child_old_price * self.child_count

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
