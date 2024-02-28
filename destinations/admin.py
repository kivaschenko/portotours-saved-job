from django.contrib import admin
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

from destinations.models import Destination, FAQDestination, ParentDestination


class FAQDestinationInline(admin.TabularInline):
    model = FAQDestination
    extra = 1
    exclude = ['updated_at']
    list_display = ['parent_name', 'priority_number']
    list_filter = ['parent_name']


class DestinationAdminForm(ModelForm):
    class Meta:
        model = Destination
        exclude = ['updated_at']
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
    inlines = [FAQDestinationInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            formset.save()


@admin.register(ParentDestination)
class ParentDestinationAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['parent_name', 'priority_number']
    list_filter = ['parent_name']


@admin.register(FAQDestination)
class FAQDestinationAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['question', 'destination', 'language', 'question', 'priority_number', 'is_active', 'updated_at']
    list_filter = ['question', 'destination', 'language', 'priority_number', 'is_active']
