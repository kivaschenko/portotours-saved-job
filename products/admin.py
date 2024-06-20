from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.contrib.gis.forms.widgets import OSMWidget
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple

from ckeditor.widgets import CKEditorWidget
from schedule.models import *  # noqa

from products.models import *  # noqa
from products.forms import ExperienceEventFormSet

# Hide exceeded models from django-scheduler
admin.site.unregister(Calendar)
admin.site.unregister(CalendarRelation)
admin.site.unregister(Occurrence)
admin.site.unregister(Event)
admin.site.unregister(EventRelation)


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


# --------
# Category

@admin.register(ExperienceCategory)
class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'slug']
    list_display = ['name', 'slug']
    list_filter = ['name']

# ---------
# TimeOfDay

@admin.register(TimeOfDay)
class TimeOfDayAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ['name', 'description']

# --------
# Duration
@admin.register(DurationForExperience)
class DurationForExperienceAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ['name', 'description']


# ----------
# Experience

@admin.register(ExperienceProvider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'short_name', 'slug', 'nif']
    search_fields = ['short_name', 'nif']


class CheckboxSelectMultipleField(ModelMultipleChoiceField):
    def __init__(self, queryset, *args, **kwargs):
        super().__init__(queryset, *args, **kwargs)
        self.widget = CheckboxSelectMultiple()


class OptionLanguageCategoryModelForm(ModelForm):
    allowed_options = CheckboxSelectMultipleField(queryset=ExperienceOption.active.all(), required=False)
    allowed_languages = CheckboxSelectMultipleField(queryset=Language.objects.all())
    categories = CheckboxSelectMultipleField(queryset=ExperienceCategory.objects.all(), required=False)
    time_of_day = CheckboxSelectMultipleField(queryset=TimeOfDay.objects.all(), required=False)
    duration = CheckboxSelectMultipleField(queryset=DurationForExperience.objects.all(), required=False)

    class Meta:
        model = ParentExperience
        exclude = ['parent_name', 'id', 'slug', 'currency', 'price', 'old_price', 'child_price', 'child_old_price',
                   'max_participants', 'is_private', 'priority_number', 'meeting_point', 'drop_point']


@admin.register(ParentExperience)
class ParentExperienceAdmin(admin.ModelAdmin):
    form = OptionLanguageCategoryModelForm
    exclude = ['updated_at', 'slug', 'meeting_point', 'drop_point', 'use_child_discount', 'use_auto_increase_old_price',
               # 'banner', 'banner_mobile', 'happy_clients_number', 'rating',
               ]
    list_display = ['id', 'parent_name', 'currency', 'price', 'old_price', 'child_price', 'child_old_price', 'second_purchase_discount',
                    'max_participants', 'is_private', 'is_exclusive', 'priority_number', 'show_on_home_page', 'is_hot_deals', 'hotel_pick_up']
    list_filter = ['parent_name', 'max_participants', 'is_private', 'is_exclusive', 'show_on_home_page', ]
    search_fields = ['parent__name', ]
    list_per_page = 20
    readonly_fields = ['child_discount', 'increase_percentage_old_price']


class ExperienceScheduleInline(admin.TabularInline):
    model = ExperienceSchedule
    extra = 1
    list_display = ['time', 'name_stop']
    list_filter = ['time', 'name_stop']


@admin.register(ExperienceImage)
class ExperienceImageAdmin(admin.ModelAdmin):
    model = ExperienceImage
    list_display = ['id', 'slider_image', 'experience']


class ExperienceImageInline(admin.TabularInline):
    model = ExperienceImage
    extra = 5


class ExperienceAdminForm(ModelForm):
    class Meta:
        model = Experience
        fields = '__all__'
        widgets = {
            'full_description': CKEditorWidget(),
            'duration': CKEditorWidget(),
            'accessibility': CKEditorWidget(),
            'possession': CKEditorWidget(),
        }


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    form = ExperienceAdminForm
    exclude = ["updated_at"]
    list_display = ['id', 'name', 'slug', 'language', 'page_title', 'is_active', 'updated_at']
    list_filter = ['name', 'slug', 'language', 'is_active', 'updated_at']
    inlines = [ExperienceImageInline, ExperienceScheduleInline]
    list_per_page = 20


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 0
    readonly_fields = ['stripe_price']
    list_display = ['experience_option', 'price', 'quantity', 'total_sum']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'random_order_number',
        'parent_experience',
        'language',
        'start_datetime',
        'status',
        'adults_count',
        'child_count',
        'total_price',
        'total_sum_with_options',
        'price_is_special',
        'old_total_price',
        'customer',
        'reported',
        'session_key',
        'created_at',
        'expired_time'
    ]
    readonly_fields = ['created_at', 'updated_at', 'parent_experience', 'language',
                       'random_order_number', 'reported', 'created_at',
                       'session_key', 'expired_time']
    list_per_page = 20
    inlines = [ProductOptionInline]


class ExperienceEventInline(admin.TabularInline):
    model = ExperienceEvent
    exclude = [
        'title',
        'description',
        'booked_participants',
        'remaining_participants',
        'color_event',
        'creator',
    ]
    formset = ExperienceEventFormSet

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.creator:
                instance.creator = request.user
            instance.save()
        formset.save_m2m()


@admin.register(Calendar)
class ExperienceCalendarAdmin(admin.ModelAdmin):
    exclude = ['name', 'slug', ]
    readonly_fields = ['is_private']
    inlines = [ExperienceEventInline]
    list_display = ['name', 'is_private']

    def is_private(self, obj):
        relation = obj.calendarrelation_set.first()
        if relation:
            parent_experience_obj = relation.content_object
            if parent_experience_obj is None:
                return 'N/A'
            if parent_experience_obj.is_private:
                return 'Private'
            else:
                return 'Group'
        return None

    is_private.short_description = 'Parent Experience is'


@admin.register(ExperienceEvent)
class ExperienceEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'max_participants', 'booked_participants',
                    'remaining_participants', 'special_price', 'child_special_price', 'total_price']
    # readonly_fields = ['title', 'max_participants', 'booked_participants', 'remaining_participants']
    search_fields = ['title', 'description', ]
    list_filter = ['start', 'calendar']
    list_per_page = 20


@admin.register(Occurrence)
class ExperienceOccurrenceAdmin(admin.ModelAdmin):
    readonly_fields = ['product_id', 'customer']
    list_display = ['id', 'product_id', 'event', 'customer', 'start', ]
    list_filter = ['start', ]
    search_fields = ['event', 'title', 'description', ]
    list_per_page = 20

    def product_id(self, obj):
        product = obj.product_set.first()
        if product is not None:
            return product.id
        return None

    def customer(self, obj):
        product = obj.product_set.first()
        if product:
            if product.customer is not None:
                return product.customer
        return None


@admin.register(ExperienceOption)
class ExperienceOptionAdmin(admin.ModelAdmin):
    readonly_fields = ('updated_at',)
    list_display = ['id', 'name', 'price', 'max_quantity', 'language', 'priority_number', 'is_active']
    list_filter = ('name', 'language', 'is_active')
    list_per_page = 20
