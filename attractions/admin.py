from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.forms import ModelForm
from django.utils.html import format_html

from ckeditor.widgets import CKEditorWidget

from attractions.models import ParentAttraction, Attraction, FAQAttraction, TagAttraction
from products.admin import CheckboxSelectMultipleField


@admin.register(TagAttraction)
class TagAttractionAdmin(ModelAdmin):
    list_display = ('id', 'display_icon', 'tag_name')

    def display_icon(self, obj):
        if obj.icon_img:
            return format_html('<img src="{}" width="30" height="30"', obj.icon_img.url)
        else:
            return "No Icon image"
    display_icon.short_description = 'Icon image'


class TagModelForm(ModelForm):
    tags = CheckboxSelectMultipleField(queryset=TagAttraction.objects.all())

    class Meta:
        model = ParentAttraction
        exclude = ['updated_at',]


class FAQAttractionInline(admin.TabularInline):
    model = FAQAttraction
    extra = 1
    exclude = ['updated_at']
    list_display = ['parent_name', 'priority_number']
    list_filter = ['parent_name']


@admin.register(ParentAttraction)
class ParentAttractionAdmin(admin.ModelAdmin):
    form = TagModelForm
    exclude = ['updated_at']
    list_display = ['id', 'parent_name', 'priority_number', 'show_on_home_page',]
    list_filter = ['parent_name']


class AttractionAdminForm(ModelForm):
    class Meta:
        model = Attraction
        exclude = ['updated_at']
        widgets = {
            'introduction_text_above_slider': CKEditorWidget(),
            'introduction_text_below_slider': CKEditorWidget(),
            'time_of_work': CKEditorWidget(),
            'address': CKEditorWidget(),
            'price': CKEditorWidget(),
            'accessibility': CKEditorWidget(),
            'possibility': CKEditorWidget(),
        }


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    form = AttractionAdminForm
    exclude = ['updated_at']
    list_display = ['id', 'name', 'slug', 'language', 'parent_attraction', 'is_active', 'updated_at']
    list_filter = ['name', 'slug', 'language', 'parent_attraction', 'is_active', 'updated_at']
    inlines = [FAQAttractionInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            formset.save()


@admin.register(FAQAttraction)
class FAQAttractionAdmin(ModelAdmin):
    exclude = ['updated_at']
    list_display = ['question', 'attraction', 'language', 'priority_number', 'is_active', 'updated_at']
    list_filter = ['question', 'attraction', 'language', 'priority_number', 'is_active']
