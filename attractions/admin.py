from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

from attractions.models import ParentAttraction, Attraction, FAQAttraction


@admin.register(ParentAttraction)
class ParentAttractionAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['parent_name', 'priority_number']
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


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    form = AttractionAdminForm
    exclude = ['updated_at']
    list_display = ['name', 'slug', 'language', 'parent_attraction', 'is_active', 'updated_at']
    list_filter = ['name', 'slug', 'language', 'parent_attraction', 'is_active', 'updated_at']


class FAQAttractionForm(ModelForm):
    class Meta:
        model = FAQAttraction
        fields = '__all__'
        widgets = {
            'answer': CKEditorWidget(),
        }
        exclude = ['updated_at']


@admin.register(FAQAttraction)
class FAQAttractionAdmin(ModelAdmin):
    form = FAQAttractionForm
    list_display = ['parent_attraction', 'language', 'question', 'priority_number', 'is_active', 'updated_at']
    list_filter = ['parent_attraction', 'language', 'question', 'priority_number', 'is_active']
