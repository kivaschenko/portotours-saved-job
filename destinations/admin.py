from django.contrib import admin
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

from destinations.models import *  # noqa


@admin.register(ParentDestination)
class ParentDestinationAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['parent_name', 'priority_number']
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
    list_display = ['name', 'slug', 'language', 'parent_destination', 'is_active', 'updated_at']
    list_filter = ['name', 'language', 'slug', 'parent_destination', 'page_title', 'is_active']


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
    list_display = ['parent_destination', 'language', 'question', 'priority_number', 'is_active', 'updated_at']
    list_filter = ['parent_destination', 'language', 'question', 'priority_number', 'is_active']
