from django.contrib import admin
from django.forms import ModelForm
from django.contrib.gis.admin import GISModelAdmin
from django.contrib.gis.forms.widgets import OSMWidget
from django.core.exceptions import ValidationError

from ckeditor.widgets import CKEditorWidget

from products.models import *  # noqa


# ------------
# MeetingPoint
class CustomOSMWidget(OSMWidget):
    template_name = "gis/openlayers-osm.html"
    default_lon = -9
    default_lat = 38
    default_zoom = 5.75

    def __init__(self, attrs=None):
        super().__init__()
        for key in ("default_lon", "default_lat", "default_zoom"):
            if not self.attrs.get(key):
                self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)


@admin.register(MeetingPoint)
class MeetingPointAdmin(GISModelAdmin):
    gis_widget = CustomOSMWidget
    gis_widget_kwargs = {}

    fields = [
        'name',
        'slug',
        'country',
        'region',
        'city',
        'address',
        'latitude',
        'longitude',
        'auto_location',
        'auto_update_address_name',
        'update_coords_by_geom',
        'geom',
        'location_raw',
    ]
    list_display = ['name', 'country', 'city', 'address', 'longitude', 'latitude', 'slug', 'geom',
                    'auto_location', 'update_coords_by_geom', 'auto_update_address_name']
    list_filter = ['name', 'country', 'region', 'city', 'address']
    readonly_fields = ['latitude', 'longitude', 'location_raw']

    def get_object(self, request, object_id, from_field=None):
        """
        Return an instance matching the field and value provided, the primary
        key is used if no field is provided. Return ``None`` if no match is
        found or the object_id fails validation.
        """
        queryset = self.get_queryset(request)
        model = queryset.model
        field = (
            model._meta.pk if from_field is None else model._meta.get_field(from_field)
        )
        try:
            object_id = field.to_python(object_id)
            obj = queryset.get(**{field.name: object_id})
            # update center coordinates for map
            if obj is not None:
                if obj.latitude is not None and obj.longitude is not None:
                    self.gis_widget_kwargs.update(
                        {'attrs': {'default_lat': obj.latitude, 'default_lon': obj.longitude, 'default_zoom': 8.75}})
            return obj
        except (model.DoesNotExist, ValidationError, ValueError):
            return None


# --------
# Language

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    fields = ['name', 'code', 'is_active']
    list_display = ['name', 'code', 'is_active']
    list_filter = ['name', 'code', 'is_active']


# -----------
# Destination

@admin.register(ParentDestination)
class ParentDestinationAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['parent_name']
    list_filter = ['parent_name']


class DestinationAdminForm(ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'
        widgets = {
            'introduction_text': CKEditorWidget(),
            'when_to_visit_text': CKEditorWidget(),
            'getting_around_text': CKEditorWidget(),
            'travel_tips_text': CKEditorWidget(),
        }


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    form = DestinationAdminForm
    exclude = ['updated_at']
    list_display = ['name', 'slug', 'language', 'is_active', 'updated_at']
    list_filter = ['name', 'language', 'slug', 'page_title', 'is_active']


class FAQDestinationAdminForm(ModelForm):
    class Meta:
        model = FAQDestination
        fields = '__all__'
        widgets = {
            'answer': CKEditorWidget(),
        }

@admin.register(FAQDestination)
class FAQDestinationAdmin(admin.ModelAdmin):
    form = FAQDestinationAdminForm
    exclude = ['updated_at']
    list_display = ['parent_destination', 'language', 'question', 'is_active', 'updated_at']
    list_filter = ['parent_destination', 'language', 'question', 'is_active']
