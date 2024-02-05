import json
import logging
from django.contrib.gis.geos import fromstr
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.urls import reverse
from django.utils.text import slugify

from geopy.geocoders import Nominatim

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
