from django.contrib import admin
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

from attractions.models import ParentAttraction, Attraction


@admin.register(ParentAttraction)
class ParentAttractionAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['parent_name']
    list_filter = ['parent_name']


class AttractionAdminForm(ModelForm):
    class Meta:
        model = Attraction
        fields = '__all__'
        widgets = {
            'introduction_text_above_slider': CKEditorWidget(),
            'introduction_text_below_slider': CKEditorWidget(),
            'time_of_work': CKEditorWidget(),
            'address': CKEditorWidget(),
            'price': CKEditorWidget(),
            'accessibility': CKEditorWidget(),
            'possibility': CKEditorWidget(),
        }

class AttractionAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['name', 'slug', 'language', 'parent_name', 'is_active', 'updated_at']
    list_filter = ['name', 'slug', 'language', 'parent_name', 'is_active', 'updated_at']
