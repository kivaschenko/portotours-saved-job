from django.contrib import admin
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

from landing_pages.models import LandingPage


class LandingPageForm(ModelForm):
    class Meta:
        model = LandingPage
        exclude = ['updated_at']
        widgets = {
            'content': CKEditorWidget(),
        }


@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    form = LandingPageForm
    exclude = ['updated_at', 'card_image']
    list_display = ['id', 'title', 'slug', 'category', 'destination', 'show_in_navbar',
                    'priority_number', 'is_active',  'updated_at']
